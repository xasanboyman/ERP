import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

def test_new_company_has_zero_debtors_and_tenant_isolation():
    # 1. Super Admin Authentication
    r = requests.post(f"{BASE_URL}/user/login", json={"username": "admin", "password": "admin"})
    assert r.status_code == 200, f"Super Admin login failed: {r.text}"
    token = r.json()["data"]["token"]
    headers = {"Authorization": token if token.startswith("Bearer ") else f"Bearer {token}"}

    # 2. Create Company A
    comp_a_code = f"CMPA_{uuid.uuid4().hex[:6]}"
    r = requests.post(f"{BASE_URL}/company/save", headers=headers, json={
        "name": f"Company A {comp_a_code}",
        "code": comp_a_code,
        "admin_username": f"admin_{comp_a_code.lower()}",
        "admin_password": "password123"
    })
    assert r.status_code == 200 and r.json().get("code") == 0, f"Failed to create Company A: {r.text}"
    comp_a_id = r.json()["data"]["id"]

    # 3. Create Company B
    comp_b_code = f"CMPB_{uuid.uuid4().hex[:6]}"
    r = requests.post(f"{BASE_URL}/company/save", headers=headers, json={
        "name": f"Company B {comp_b_code}",
        "code": comp_b_code,
        "admin_username": f"admin_{comp_b_code.lower()}",
        "admin_password": "password123"
    })
    assert r.status_code == 200 and r.json().get("code") == 0, f"Failed to create Company B: {r.text}"
    comp_b_id = r.json()["data"]["id"]

    try:
        # 4. Login as Company A admin
        r = requests.post(f"{BASE_URL}/user/login", json={"username": f"admin_{comp_a_code.lower()}", "password": "password123"})
        assert r.status_code == 200 and r.json().get("code") == 0
        token_a = r.json()["data"]["token"]
        headers_a = {"Authorization": token_a if token_a.startswith("Bearer ") else f"Bearer {token_a}"}

        # 5. Verify Company A has EXACTLY 0 debtors
        r = requests.get(f"{BASE_URL}/sales/debtors", headers=headers_a)
        data_a = r.json().get("data", {})
        print("Company A initial debtors:", data_a)
        assert data_a.get("active_debtors_count") == 0, f"Expected 0 active debtors, got {data_a.get('active_debtors_count')}"
        assert len(data_a.get("list", [])) == 0, f"Expected empty debtors list, got {data_a.get('list')}"
        assert data_a.get("total_debt") == 0, f"Expected 0 total debt, got {data_a.get('total_debt')}"

        # 6. Login as Company B admin
        r = requests.post(f"{BASE_URL}/user/login", json={"username": f"admin_{comp_b_code.lower()}", "password": "password123"})
        assert r.status_code == 200 and r.json().get("code") == 0
        token_b = r.json()["data"]["token"]
        headers_b = {"Authorization": token_b if token_b.startswith("Bearer ") else f"Bearer {token_b}"}

        # 7. Verify Company B also has EXACTLY 0 debtors
        r = requests.get(f"{BASE_URL}/sales/debtors", headers=headers_b)
        data_b = r.json().get("data", {})
        print("Company B initial debtors:", data_b)
        assert data_b.get("active_debtors_count") == 0
        assert len(data_b.get("list", [])) == 0
        assert data_b.get("total_debt") == 0

        # Verify no hardcoded debtors appear
        names_a = [d["name"] for d in data_a.get("list", [])]
        assert "Jamshid Aka" not in names_a
        assert "Otabek Rahimov" not in names_a
        assert "Kassir_Sardor" not in names_a

        print("Verification passed: New companies start with 0 debtors and no mock seed data!")

    finally:
        # Cleanup
        requests.post(f"{BASE_URL}/company/delete", headers=headers, json={"company_id": comp_a_id, "admin_password": "admin"})
        requests.post(f"{BASE_URL}/company/delete", headers=headers, json={"company_id": comp_b_id, "admin_password": "admin"})
        print("Cleaned up test companies A & B.")

if __name__ == "__main__":
    test_new_company_has_zero_debtors_and_tenant_isolation()
    print("ALL TESTS PASSED SUCCESSFULLY!")
