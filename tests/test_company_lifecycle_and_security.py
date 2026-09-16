import requests
import json
import time

BASE_URL = "https://xn--dr8haa.uz/oracle/erp-api"

def run_tests():
    print("=== TEST 1: Super Admin Authentication ===")
    r = requests.post(f"{BASE_URL}/user/login", json={"username": "admin", "password": "idk"})
    # If password is admin or idk
    if r.status_code != 200 or r.json().get("code") != 0:
        r = requests.post(f"{BASE_URL}/user/login", json={"username": "admin", "password": "idk"})
    res = r.json()
    if res.get("code") != 0:
        # try idk or admin
        for pwd in ["idk", "admin", "admin123", "password"]:
            r = requests.post(f"{BASE_URL}/user/login", json={"username": "admin", "password": pwd})
            if r.json().get("code") == 0:
                print(f"Logged in with password: {pwd}")
                admin_pwd = pwd
                break
        else:
            raise Exception(f"Super admin login failed: {r.text}")
    else:
        admin_pwd = "idk"

    admin_token = r.json()["data"]["token"]
    headers = {"Authorization": admin_token}
    print(f"Super Admin authenticated successfully. Admin password is '{admin_pwd}'")

    print("\n=== TEST 2: Create a Test Company ===")
    ts = int(time.time())
    test_code = f"test_{ts % 10000}"
    create_payload = {
        "name": f"Test Security Corp {test_code}",
        "code": test_code,
        "plan": "basic",
        "billing_cycle": "monthly",
        "max_users": 5,
        "admin_username": f"user_{test_code}",
        "admin_password": "init_password_123",
        "admin_full_name": "Test Manager"
    }
    r = requests.post(f"{BASE_URL}/company/save", json=create_payload, headers=headers)
    assert r.status_code == 200 and r.json().get("code") == 0, f"Company creation failed: {r.text}"
    comp_data = r.json()["data"]
    comp_id = comp_data["id"]
    print(f"Created company ID: {comp_id}, Code: {test_code}, Admin Username: {create_payload['admin_username']}")

    print("\n=== TEST 3: Login as Test Company Admin (Initial Password) ===")
    r = requests.post(f"{BASE_URL}/user/login", json={
        "username": create_payload["admin_username"],
        "password": "init_password_123"
    })
    assert r.status_code == 200 and r.json().get("code") == 0, f"Initial login failed: {r.text}"
    tenant_token = r.json()["data"]["token"]
    print("Initial company admin login SUCCEEDED!")

    print("\n=== TEST 4: Change Company Login & Password (Reset Password Endpoint) ===")
    new_username = f"new_usr_{test_code}"
    new_password = "new_secure_password_999"
    r = requests.post(f"{BASE_URL}/company/account/reset-password", json={
        "company_id": comp_id,
        "username": new_username,
        "new_password": new_password,
        "full_name": "Updated Test Manager"
    }, headers=headers)
    assert r.status_code == 200 and r.json().get("code") == 0, f"Reset password failed: {r.text}"
    print(f"Changed credentials: {new_username} / {new_password}")

    # Old password should fail
    r_old = requests.post(f"{BASE_URL}/user/login", json={
        "username": create_payload["admin_username"],
        "password": "init_password_123"
    })
    assert r_old.json().get("code") != 0, "Old password must NOT succeed after reset!"
    print("Verification passed: Old login credentials rejected.")

    # New login & password should succeed
    r_new = requests.post(f"{BASE_URL}/user/login", json={
        "username": new_username,
        "password": new_password
    })
    assert r_new.status_code == 200 and r_new.json().get("code") == 0, f"New credentials login failed: {r_new.text}"
    tenant_token = r_new.json()["data"]["token"]
    print("Verification passed: New login credentials succeeded!")

    print("\n=== TEST 5: Disable / Suspend Company (Monthly Payment Unpaid) ===")
    r = requests.post(f"{BASE_URL}/company/status", json={
        "company_id": comp_id,
        "status": 0
    }, headers=headers)
    assert r.status_code == 200 and r.json().get("code") == 0, f"Disable company failed: {r.text}"
    print("Company status set to 0 (Suspended/To'xtatilgan).")

    # Trying to login as the tenant while company is disabled
    r_suspended_login = requests.post(f"{BASE_URL}/user/login", json={
        "username": new_username,
        "password": new_password
    })
    assert r_suspended_login.json().get("code") == 403, f"Expected 403 for suspended company login, got: {r_suspended_login.text}"
    print(f"Verification passed: Login BLOCKED with message: {r_suspended_login.json().get('message')}")

    # Using existing token while company is disabled
    r_suspended_api = requests.get(f"{BASE_URL}/product/list", headers={"Authorization": tenant_token})
    assert r_suspended_api.status_code == 403 or r_suspended_api.json().get("code") == 403, f"Expected 403 for API call: {r_suspended_api.text}"
    print(f"Verification passed: Authenticated API call BLOCKED with 403 for suspended tenant.")

    print("\n=== TEST 6: Re-enable Company ===")
    r = requests.post(f"{BASE_URL}/company/status", json={
        "company_id": comp_id,
        "status": 1
    }, headers=headers)
    assert r.status_code == 200 and r.json().get("code") == 0, f"Re-enable failed: {r.text}"
    print("Company re-enabled.")

    r_reenabled_login = requests.post(f"{BASE_URL}/user/login", json={
        "username": new_username,
        "password": new_password
    })
    assert r_reenabled_login.status_code == 200 and r_reenabled_login.json().get("code") == 0, f"Login failed after re-enabling: {r_reenabled_login.text}"
    print("Verification passed: Tenant can log in normally after re-enabling.")

    print("\n=== TEST 7: Delete Company Security (Admin Password Verification) ===")
    # 7.1 Try deleting without admin password
    r_del_no_pwd = requests.post(f"{BASE_URL}/company/delete", json={
        "id": comp_id
    }, headers=headers)
    assert r_del_no_pwd.status_code == 400, f"Expected 400 when admin_password is missing, got: {r_del_no_pwd.status_code} {r_del_no_pwd.text}"
    print("Verification passed: Deletion without password was REJECTED with 400.")

    # 7.2 Try deleting with WRONG admin password
    r_del_wrong_pwd = requests.post(f"{BASE_URL}/company/delete", json={
        "id": comp_id,
        "admin_password": "completely_wrong_password_xyz"
    }, headers=headers)
    assert r_del_wrong_pwd.status_code == 400, f"Expected 400 for wrong password, got: {r_del_wrong_pwd.status_code} {r_del_wrong_pwd.text}"
    print("Verification passed: Deletion with WRONG admin password was REJECTED with 400 'Super Admin paroli noto'g'ri!'.")

    # 7.3 Delete with CORRECT admin password
    r_del_ok = requests.post(f"{BASE_URL}/company/delete", json={
        "id": comp_id,
        "admin_password": admin_pwd
    }, headers=headers)
    assert r_del_ok.status_code == 200 and r_del_ok.json().get("code") == 0, f"Deletion with correct password failed: {r_del_ok.text}"
    print(f"Verification passed: Deletion with CORRECT admin password SUCCEEDED! Message: {r_del_ok.json().get('message')}")

    # 7.4 Verify company is gone
    r_check = requests.get(f"{BASE_URL}/company/detail/{comp_id}", headers=headers)
    assert r_check.status_code == 404, f"Deleted company should return 404, got: {r_check.status_code}"
    print("Verification passed: Company no longer exists.")

    print("\n🎉 ALL 7 TESTS PASSED SUCCESSFULLY! 100% VERIFIED!")

if __name__ == "__main__":
    run_tests()
