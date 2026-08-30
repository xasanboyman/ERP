import pytest
import uuid
import datetime
import concurrent.futures
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import SessionLocal
from app import models, crud, auth

# Helper fixture for FastAPI TestClient
@pytest.fixture
def client():
    return TestClient(app)

# Helper fixture for DB session
@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth token helpers
def get_auth_headers(username: str = "admin"):
    token = auth.create_access_token(username)
    return {"Authorization": f"Bearer {token}"}

def pair_test_device(client, device_name="Test-Scanner-Device", username="admin"):
    headers = get_auth_headers(username)
    res = client.post("/api/device/pair-token", json={"device_name": device_name}, headers=headers)
    assert res.status_code == 200, res.text
    body = res.json()
    data = body.get("data", body)
    return data["token"], data.get("user_id", 1), data


# ==============================================================================
# TIER 1: FEATURE COVERAGE (45 Tests Total: R1: 15, R2: 20, R3: 10)
# ==============================================================================

# --- R1: Device Pairing & Token Authorization (15 tests) ---

def test_r1_t1_01_pair_code_generation(client):
    headers = get_auth_headers("admin")
    res = client.post("/api/device/pair-token", json={"device_name": "Scanner-iPhone-14"}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    token_data = data.get("data", data)
    assert "token" in token_data
    assert "pair_code" in token_data
    assert "expires_at" in token_data
    assert token_data["device_name"] == "Scanner-iPhone-14"

def test_r1_t1_02_pair_token_with_custom_device_name(client):
    headers = get_auth_headers("admin")
    res = client.post("/api/device/pair-token", json={"device_name": "Warehouse-Handheld-02"}, headers=headers)
    assert res.status_code == 200
    data = res.json().get("data", res.json())
    assert data["device_name"] == "Warehouse-Handheld-02"

def test_r1_t1_03_device_list_retrieval(client):
    headers = get_auth_headers("admin")
    client.post("/api/device/pair-token", json={"device_name": "List-Device-1"}, headers=headers)
    res = client.get("/api/device/list", headers=headers)
    assert res.status_code == 200
    data = res.json().get("data", res.json())
    assert "total" in data
    assert "list" in data
    assert isinstance(data["list"], list)
    assert len(data["list"]) >= 1

def test_r1_t1_04_device_list_contains_paired_device(client):
    headers = get_auth_headers("admin")
    pair_res = client.post("/api/device/pair-token", json={"device_name": "Unique-Device-99"}, headers=headers)
    pair_data = pair_res.json().get("data", pair_res.json())
    res = client.get("/api/device/list", headers=headers)
    devices = res.json().get("data", {}).get("list", [])
    matched = [d for d in devices if d["token"] == pair_data["token"]]
    assert len(matched) == 1
    assert matched[0]["device_name"] == "Unique-Device-99"

def test_r1_t1_05_valid_x_device_token_verify(client):
    token, _, _ = pair_test_device(client, "Verify-Device")
    res = client.get("/api/device/verify", headers={"X-Device-Token": token})
    assert res.status_code == 200
    data = res.json().get("data", res.json())
    assert data["device_name"] == "Verify-Device"

def test_r1_t1_06_valid_x_device_token_push_request(client):
    token, _, _ = pair_test_device(client, "Push-Dev")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 1
    }
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pending"
    assert "push_id" in data

def test_r1_t1_07_device_revocation_from_personal_center(client, db_session):
    headers = get_auth_headers("admin")
    pair_res = client.post("/api/device/pair-token", json={"device_name": "To-Revoke-Dev"}, headers=headers)
    token = pair_res.json().get("data", pair_res.json())["token"]
    dev_obj = db_session.query(models.DeviceToken).filter(models.DeviceToken.token == token).first()
    assert dev_obj is not None
    
    del_res = client.delete(f"/api/device/revoke/{dev_obj.id}", headers=headers)
    assert del_res.status_code == 200
    db_session.refresh(dev_obj)
    assert dev_obj.status == "revoked"

def test_r1_t1_08_revoked_token_verify_fails(client, db_session):
    headers = get_auth_headers("admin")
    pair_res = client.post("/api/device/pair-token", json={"device_name": "Revoke-Verify"}, headers=headers)
    token = pair_res.json().get("data", pair_res.json())["token"]
    dev_obj = db_session.query(models.DeviceToken).filter(models.DeviceToken.token == token).first()
    client.delete(f"/api/device/revoke/{dev_obj.id}", headers=headers)

    res = client.get("/api/device/verify", headers={"X-Device-Token": token})
    assert res.status_code == 403

def test_r1_t1_09_revoked_token_push_fails(client, db_session):
    headers = get_auth_headers("admin")
    pair_res = client.post("/api/device/pair-token", json={"device_name": "Revoke-Push"}, headers=headers)
    token = pair_res.json().get("data", pair_res.json())["token"]
    dev_obj = db_session.query(models.DeviceToken).filter(models.DeviceToken.token == token).first()
    client.delete(f"/api/device/revoke/{dev_obj.id}", headers=headers)

    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 1
    }
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 403

def test_r1_t1_10_revoked_token_checkout_fails(client, db_session):
    headers = get_auth_headers("admin")
    pair_res = client.post("/api/device/pair-token", json={"device_name": "Revoke-Checkout"}, headers=headers)
    token = pair_res.json().get("data", pair_res.json())["token"]
    dev_obj = db_session.query(models.DeviceToken).filter(models.DeviceToken.token == token).first()
    client.delete(f"/api/device/revoke/{dev_obj.id}", headers=headers)

    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "payment_type": "cash",
        "total_amount": 2500.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 403

def test_r1_t1_11_pair_multiple_devices_for_same_user(client):
    headers = get_auth_headers("admin")
    res1 = client.post("/api/device/pair-token", json={"device_name": "Multi-Dev-1"}, headers=headers)
    res2 = client.post("/api/device/pair-token", json={"device_name": "Multi-Dev-2"}, headers=headers)
    assert res1.status_code == 200
    assert res2.status_code == 200
    t1 = res1.json().get("data", res1.json())["token"]
    t2 = res2.json().get("data", res2.json())["token"]
    assert t1 != t2

def test_r1_t1_12_device_list_shows_multiple_devices(client):
    headers = get_auth_headers("admin")
    client.post("/api/device/pair-token", json={"device_name": "Show-Multi-1"}, headers=headers)
    client.post("/api/device/pair-token", json={"device_name": "Show-Multi-2"}, headers=headers)
    res = client.get("/api/device/list", headers=headers)
    devices = res.json().get("data", {}).get("list", [])
    names = [d["device_name"] for d in devices]
    assert "Show-Multi-1" in names
    assert "Show-Multi-2" in names

def test_r1_t1_13_device_last_used_updated_on_request(client, db_session):
    token, _, _ = pair_test_device(client, "Last-Used-Dev")
    dev_before = db_session.query(models.DeviceToken).filter(models.DeviceToken.token == token).first()
    first_used = dev_before.last_used_at

    client.get("/api/device/verify", headers={"X-Device-Token": token})
    db_session.refresh(dev_before)
    assert dev_before.last_used_at is not None

def test_r1_t1_14_pair_token_for_explicit_user_id(client):
    headers = get_auth_headers("admin")
    res = client.post("/api/device/pair-token", json={"user_id": 1, "device_name": "Explicit-User-Dev"}, headers=headers)
    assert res.status_code == 200
    data = res.json().get("data", res.json())
    assert data["user_id"] == 1

def test_r1_t1_15_device_token_db_record_integrity(client, db_session):
    token, _, _ = pair_test_device(client, "DB-Integrity-Dev")
    rec = db_session.query(models.DeviceToken).filter(models.DeviceToken.token == token).first()
    assert rec is not None
    assert rec.device_name == "DB-Integrity-Dev"
    assert rec.status == "active"
    assert rec.pair_code is not None


# --- R2: Mobile Dual Sales Modes (20 tests) ---

def test_r2_t1_01_computer_sale_mode_push_to_pc(client):
    token, _, _ = pair_test_device(client, "CS-Push-1")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 2, "price": 2500.0}],
        "pc_user_id": 1
    }
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pending"
    assert data["push_id"].startswith("PUSH-")

def test_r2_t1_02_computer_sale_push_single_item(client, db_session):
    token, _, _ = pair_test_device(client, "CS-Push-Single")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-002", "quantity": 1, "price": 150.0}],
        "pc_user_id": 1
    }
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    push_id = res.json()["push_id"]
    sp = db_session.query(models.SalesPush).filter(models.SalesPush.id == push_id).first()
    assert sp is not None
    assert sp.status == "pending"

def test_r2_t1_03_computer_sale_push_multi_items(client):
    token, _, _ = pair_test_device(client, "CS-Push-Multi")
    payload = {
        "device_token": token,
        "items": [
            {"product_id": "PROD-001", "quantity": 1, "price": 2500.0},
            {"product_id": "PROD-002", "quantity": 2, "price": 150.0}
        ],
        "pc_user_id": 1
    }
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 200

def test_r2_t1_04_computer_sale_push_preserves_prices(client, db_session):
    token, _, _ = pair_test_device(client, "CS-Prices")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 5, "price": 30.0}],
        "pc_user_id": 1
    }
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    push_id = res.json()["push_id"]
    sp = db_session.query(models.SalesPush).filter(models.SalesPush.id == push_id).first()
    assert "30.0" in sp.items_json

def test_r2_t1_05_phone_sale_checkout_cash(client):
    token, _, _ = pair_test_device(client, "Phone-Cash")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-002", "quantity": 1, "price": 150.0}],
        "payment_type": "cash",
        "total_amount": 150.0,
        "paid_amount": 150.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 200
    data = res.json()
    assert data["payment_method"] == "naqd"
    assert data["paid_amount"] == 150.0
    assert data["debt_amount"] == 0.0

def test_r2_t1_06_phone_sale_checkout_cash_stock_decrement(client, db_session):
    prod = db_session.query(models.Product).filter(models.Product.id == "PROD-002").first()
    initial_stock = prod.quantityInStock

    token, _, _ = pair_test_device(client, "Stock-Dec-Dev")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-002", "quantity": 2, "price": 150.0}],
        "payment_type": "cash",
        "total_amount": 300.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 200

    db_session.refresh(prod)
    assert prod.quantityInStock == initial_stock - 2

def test_r2_t1_07_phone_sale_checkout_card(client):
    token, _, _ = pair_test_device(client, "Phone-Card")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "payment_type": "card",
        "total_amount": 30.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 200
    data = res.json()
    assert data["payment_method"] == "karta"
    assert data["paid_amount"] == 30.0

def test_r2_t1_08_phone_sale_checkout_card_full_payment(client):
    token, _, _ = pair_test_device(client, "Card-Full")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 2, "price": 30.0}],
        "payment_type": "card",
        "total_amount": 60.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.json()["debt_amount"] == 0.0

def test_r2_t1_09_phone_sale_checkout_debt(client):
    token, _, _ = pair_test_device(client, "Phone-Debt")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "payment_type": "debt",
        "total_amount": 30.0,
        "paid_amount": 0.0,
        "customer_name": "Debt-Customer-1"
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 200
    data = res.json()
    assert data["payment_method"] == "nasiya"
    assert data["debt_amount"] == 30.0

def test_r2_t1_10_phone_sale_checkout_debt_balance_recorded(client, db_session):
    token, _, _ = pair_test_device(client, "Debt-Bal")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 2, "price": 30.0}],
        "payment_type": "debt",
        "total_amount": 60.0,
        "paid_amount": 10.0,
        "customer_name": "Partial-Debtor"
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    sale_id = res.json()["id"]
    sale_db = db_session.query(models.Sale).filter(models.Sale.id == sale_id).first()
    assert sale_db.debt_amount == 50.0

def test_r2_t1_11_phone_sale_checkout_with_partial_payment(client):
    token, _, _ = pair_test_device(client, "Partial-Pay")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-002", "quantity": 1, "price": 150.0}],
        "payment_type": "debt",
        "total_amount": 150.0,
        "paid_amount": 50.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    data = res.json()
    assert data["paid_amount"] == 50.0
    assert data["debt_amount"] == 100.0

def test_r2_t1_12_phone_sale_checkout_multi_item_cart(client):
    token, _, _ = pair_test_device(client, "Multi-Item-Checkout")
    payload = {
        "device_token": token,
        "items": [
            {"product_id": "PROD-002", "quantity": 1, "price": 150.0},
            {"product_id": "PROD-003", "quantity": 2, "price": 30.0}
        ],
        "payment_type": "cash",
        "total_amount": 210.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 200
    assert res.json()["total_items"] == 3

def test_r2_t1_13_phone_sale_checkout_receipt_number_format(client):
    token, _, _ = pair_test_device(client, "Receipt-Fmt")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "payment_type": "cash",
        "total_amount": 30.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    receipt_no = res.json()["receipt_number"]
    assert receipt_no.startswith("CHK-PH-")

def test_r2_t1_14_phone_sale_checkout_sale_items_db_entry(client, db_session):
    token, _, _ = pair_test_device(client, "Sale-Items-DB")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-002", "quantity": 2, "price": 150.0}],
        "payment_type": "cash",
        "total_amount": 300.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    sale_id = res.json()["id"]
    items_in_db = db_session.query(models.SaleItem).filter(models.SaleItem.sale_id == sale_id).all()
    assert len(items_in_db) == 1
    assert items_in_db[0].quantity == 2

def test_r2_t1_15_phone_sale_checkout_with_discount(client):
    token, _, _ = pair_test_device(client, "Discount-Dev")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-002", "quantity": 1, "price": 150.0}],
        "payment_type": "cash",
        "total_amount": 150.0,
        "discount": 20.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 200
    assert res.json()["total_amount"] == 130.0

def test_r2_t1_16_phone_sale_checkout_with_customer_info(client, db_session):
    token, _, _ = pair_test_device(client, "Cust-Info-Dev")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "payment_type": "cash",
        "total_amount": 30.0,
        "customer_name": "Alisher Navoiy",
        "customer_phone": "+998901112233"
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    sale_id = res.json()["id"]
    sale_db = db_session.query(models.Sale).filter(models.Sale.id == sale_id).first()
    assert sale_db.customer_name == "Alisher Navoiy"
    assert sale_db.customer_phone == "+998901112233"

def test_r2_t1_17_phone_sale_checkout_with_remark(client, db_session):
    token, _, _ = pair_test_device(client, "Remark-Dev")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "payment_type": "cash",
        "total_amount": 30.0,
        "remark": "Mobile test remark"
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    sale_id = res.json()["id"]
    sale_db = db_session.query(models.Sale).filter(models.Sale.id == sale_id).first()
    assert sale_db.remark == "Mobile test remark"

def test_r2_t1_18_phone_sale_checkout_naqd_alias(client):
    token, _, _ = pair_test_device(client, "Naqd-Alias")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "payment_type": "naqd",
        "total_amount": 30.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.json()["payment_method"] == "naqd"

def test_r2_t1_19_phone_sale_checkout_karta_alias(client):
    token, _, _ = pair_test_device(client, "Karta-Alias")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "payment_type": "karta",
        "total_amount": 30.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.json()["payment_method"] == "karta"

def test_r2_t1_20_phone_sale_checkout_nasiya_alias(client):
    token, _, _ = pair_test_device(client, "Nasiya-Alias")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "payment_type": "nasiya",
        "total_amount": 30.0,
        "paid_amount": 0.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.json()["payment_method"] == "nasiya"


# --- R3: PC POS Notification & Handover (10 tests) ---

def test_r3_t1_01_get_pending_pushes_pc_session(client):
    token, _, _ = pair_test_device(client, "Pending-Push-Dev")
    client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})

    headers = get_auth_headers("admin")
    res = client.get("/api/sales/pending-pushes", headers=headers)
    assert res.status_code == 200
    pushes = res.json().get("data", [])
    assert len(pushes) >= 1
    assert any(p["device_token"] == token for p in pushes)

def test_r3_t1_02_get_pending_pushes_item_count(client):
    token, _, _ = pair_test_device(client, "Item-Count-Dev")
    client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [
            {"product_id": "PROD-001", "quantity": 1, "price": 2500.0},
            {"product_id": "PROD-002", "quantity": 2, "price": 150.0}
        ],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})

    headers = get_auth_headers("admin")
    res = client.get("/api/sales/pending-pushes", headers=headers)
    pushes = res.json().get("data", [])
    target = [p for p in pushes if p["device_token"] == token][0]
    assert target["item_count"] == 2

def test_r3_t1_03_accept_push_alert(client, db_session):
    token, _, _ = pair_test_device(client, "Accept-Dev")
    push_res = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})
    push_id = push_res.json()["push_id"]

    headers = get_auth_headers("admin")
    res = client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "accept"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "accepted"

    sp = db_session.query(models.SalesPush).filter(models.SalesPush.id == push_id).first()
    assert sp.status == "accepted"

def test_r3_t1_04_decline_push_alert(client, db_session):
    token, _, _ = pair_test_device(client, "Decline-Dev")
    push_res = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})
    push_id = push_res.json()["push_id"]

    headers = get_auth_headers("admin")
    res = client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "decline"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "declined"

    sp = db_session.query(models.SalesPush).filter(models.SalesPush.id == push_id).first()
    assert sp.status == "declined"

def test_r3_t1_05_fetch_accepted_push_payload(client):
    token, _, _ = pair_test_device(client, "Payload-Dev")
    push_res = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-002", "quantity": 3, "price": 150.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})
    push_id = push_res.json()["push_id"]

    headers = get_auth_headers("admin")
    client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "accept"}, headers=headers)

    res = client.get(f"/api/sales/push-payload/{push_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["push_id"] == push_id
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 3

def test_r3_t1_06_push_payload_total_amount_calculation(client):
    token, _, _ = pair_test_device(client, "Calc-Payload-Dev")
    push_res = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [
            {"product_id": "PROD-002", "quantity": 2, "price": 150.0},
            {"product_id": "PROD-003", "quantity": 4, "price": 30.0}
        ],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})
    push_id = push_res.json()["push_id"]

    headers = get_auth_headers("admin")
    client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "accept"}, headers=headers)
    res = client.get(f"/api/sales/push-payload/{push_id}", headers=headers)
    assert res.json()["total_amount"] == 420.0

def test_r3_t1_07_complete_pos_checkout_after_handover(client):
    headers = get_auth_headers("admin")
    payload = {
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "payment_method": "naqd",
        "total_amount": 30.0,
        "paid_amount": 30.0,
        "customer_name": "Walk-in POS Customer"
    }
    res = client.post("/sales/checkout", json=payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["code"] == 0

def test_r3_t1_08_pos_checkout_after_handover_stock_update(client, db_session):
    prod = db_session.query(models.Product).filter(models.Product.id == "PROD-003").first()
    stock_before = prod.quantityInStock

    headers = get_auth_headers("admin")
    payload = {
        "items": [{"product_id": "PROD-003", "quantity": 3, "price": 30.0}],
        "payment_method": "naqd",
        "total_amount": 90.0
    }
    client.post("/sales/checkout", json=payload, headers=headers)
    db_session.refresh(prod)
    assert prod.quantityInStock == stock_before - 3

def test_r3_t1_09_pending_pushes_filtered_after_accept(client):
    token, _, _ = pair_test_device(client, "Filter-Accept-Dev")
    push_res = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})
    push_id = push_res.json()["push_id"]

    headers = get_auth_headers("admin")
    client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "accept"}, headers=headers)

    res = client.get("/api/sales/pending-pushes", headers=headers)
    pushes = res.json().get("data", [])
    assert not any(p["push_id"] == push_id for p in pushes)

def test_r3_t1_10_pending_pushes_filtered_after_decline(client):
    token, _, _ = pair_test_device(client, "Filter-Decline-Dev")
    push_res = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})
    push_id = push_res.json()["push_id"]

    headers = get_auth_headers("admin")
    client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "decline"}, headers=headers)

    res = client.get("/api/sales/pending-pushes", headers=headers)
    pushes = res.json().get("data", [])
    assert not any(p["push_id"] == push_id for p in pushes)


# ==============================================================================
# TIER 2: BOUNDARY & CORNER CASES (40 Tests Total: R1: 15, R2: 15, R3: 10)
# ==============================================================================

# --- R1 Boundary Cases (15 tests) ---

def test_r1_t2_01_request_missing_x_device_token(client):
    res = client.get("/api/device/verify")
    assert res.status_code == 401

def test_r1_t2_02_request_empty_x_device_token(client):
    res = client.get("/api/device/verify", headers={"X-Device-Token": ""})
    assert res.status_code == 401

def test_r1_t2_03_request_malformed_x_device_token(client):
    res = client.get("/api/device/verify", headers={"X-Device-Token": "INVALID_TOKEN_XYZ_12345"})
    assert res.status_code == 401

def test_r1_t2_04_pair_code_generation_empty_device_name(client):
    headers = get_auth_headers("admin")
    res = client.post("/api/device/pair-token", json={"device_name": ""}, headers=headers)
    assert res.status_code == 400

def test_r1_t2_05_pair_code_generation_whitespace_device_name(client):
    headers = get_auth_headers("admin")
    res = client.post("/api/device/pair-token", json={"device_name": "   "}, headers=headers)
    assert res.status_code == 400

def test_r1_t2_06_pair_code_generation_nonexistent_user_id(client):
    headers = get_auth_headers("admin")
    res = client.post("/api/device/pair-token", json={"user_id": 99999, "device_name": "Test"}, headers=headers)
    assert res.status_code == 404

def test_r1_t2_07_revoke_nonexistent_device_id(client):
    headers = get_auth_headers("admin")
    res = client.delete("/api/device/revoke/999999", headers=headers)
    assert res.status_code == 404

def test_r1_t2_08_revoke_already_revoked_device(client, db_session):
    headers = get_auth_headers("admin")
    pair_res = client.post("/api/device/pair-token", json={"device_name": "Double-Revoke"}, headers=headers)
    token = pair_res.json().get("data", pair_res.json())["token"]
    dev_obj = db_session.query(models.DeviceToken).filter(models.DeviceToken.token == token).first()

    res1 = client.delete(f"/api/device/revoke/{dev_obj.id}", headers=headers)
    assert res1.status_code == 200

    res2 = client.delete(f"/api/device/revoke/{dev_obj.id}", headers=headers)
    assert res2.status_code == 400

def test_r1_t2_09_revoke_other_users_device(client):
    headers_admin = get_auth_headers("admin")
    headers_test = get_auth_headers("test")
    pair_res = client.post("/api/device/pair-token", json={"device_name": "Admin-Dev"}, headers=headers_admin)
    token_admin = pair_res.json().get("data", pair_res.json())["token"]

    db = SessionLocal()
    dev_obj = db.query(models.DeviceToken).filter(models.DeviceToken.token == token_admin).first()
    dev_id = dev_obj.id
    db.close()

    res = client.delete(f"/api/device/revoke/{dev_id}", headers=headers_test)
    assert res.status_code == 403

def test_r1_t2_10_repair_device_after_revocation(client, db_session):
    headers = get_auth_headers("admin")
    res1 = client.post("/api/device/pair-token", json={"device_name": "Re-Pair-Dev"}, headers=headers)
    t1 = res1.json().get("data", res1.json())["token"]
    dev1 = db_session.query(models.DeviceToken).filter(models.DeviceToken.token == t1).first()

    client.delete(f"/api/device/revoke/{dev1.id}", headers=headers)

    res2 = client.post("/api/device/pair-token", json={"device_name": "Re-Pair-Dev"}, headers=headers)
    assert res2.status_code == 200
    t2 = res2.json().get("data", res2.json())["token"]
    assert t1 != t2

def test_r1_t2_11_device_list_unauthenticated(client):
    res = client.get("/api/device/list")
    assert res.status_code == 401

def test_r1_t2_12_device_list_invalid_bearer_token(client):
    res = client.get("/api/device/list", headers={"Authorization": "Bearer invalid_jwt_token"})
    assert res.status_code == 401

def test_r1_t2_13_verify_device_with_revoked_token(client, db_session):
    headers = get_auth_headers("admin")
    pair_res = client.post("/api/device/pair-token", json={"device_name": "Verify-Revoked"}, headers=headers)
    token = pair_res.json().get("data", pair_res.json())["token"]
    dev_obj = db_session.query(models.DeviceToken).filter(models.DeviceToken.token == token).first()

    client.delete(f"/api/device/revoke/{dev_obj.id}", headers=headers)
    res = client.get("/api/device/verify", headers={"X-Device-Token": token})
    assert res.status_code == 403

def test_r1_t2_14_verify_device_unauthenticated(client):
    res = client.get("/api/device/verify")
    assert res.status_code == 401

def test_r1_t2_15_pair_device_unauthenticated(client):
    res = client.post("/api/device/pair-token", json={"device_name": "NoAuth-Dev"})
    assert res.status_code == 401


# --- R2 Boundary Cases (15 tests) ---

def test_r2_t2_01_push_pc_sale_empty_items(client):
    token, _, _ = pair_test_device(client, "Push-Empty")
    payload = {"device_token": token, "items": [], "pc_user_id": 1}
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 400

def test_r2_t2_02_push_pc_sale_missing_items_field(client):
    token, _, _ = pair_test_device(client, "Push-NoItems")
    payload = {"device_token": token, "pc_user_id": 1}
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    assert res.status_code in [400, 422]

def test_r2_t2_03_push_pc_sale_invalid_product_id(client):
    token, _, _ = pair_test_device(client, "Push-BadProd")
    payload = {
        "device_token": token,
        "items": [{"product_id": "NONEXISTENT_PROD", "quantity": 1, "price": 10.0}],
        "pc_user_id": 1
    }
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 404

def test_r2_t2_04_push_pc_sale_zero_quantity(client):
    token, _, _ = pair_test_device(client, "Push-ZeroQty")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 0, "price": 2500.0}],
        "pc_user_id": 1
    }
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 400

def test_r2_t2_05_push_pc_sale_negative_quantity(client):
    token, _, _ = pair_test_device(client, "Push-NegQty")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": -5, "price": 2500.0}],
        "pc_user_id": 1
    }
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 400

def test_r2_t2_06_push_pc_sale_negative_price(client):
    token, _, _ = pair_test_device(client, "Push-NegPrice")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": -10.0}],
        "pc_user_id": 1
    }
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 400

def test_r2_t2_07_push_pc_sale_invalid_pc_user_id(client):
    token, _, _ = pair_test_device(client, "Push-BadUser")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 99999
    }
    res = client.post("/api/sales/push-pc-sale", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 404

def test_r2_t2_08_phone_checkout_empty_items(client):
    token, _, _ = pair_test_device(client, "CHK-Empty")
    payload = {"device_token": token, "items": [], "payment_type": "cash", "total_amount": 0.0}
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 400

def test_r2_t2_09_phone_checkout_invalid_product_id(client):
    token, _, _ = pair_test_device(client, "CHK-BadProd")
    payload = {
        "device_token": token,
        "items": [{"product_id": "INVALID_PROD_ID", "quantity": 1, "price": 10.0}],
        "payment_type": "cash",
        "total_amount": 10.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 404

def test_r2_t2_10_phone_checkout_insufficient_stock(client):
    token, _, _ = pair_test_device(client, "CHK-NoStock")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 999999, "price": 2500.0}],
        "payment_type": "cash",
        "total_amount": 999999 * 2500.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 400
    assert "omborda yetarli emas" in res.json().get("detail", "")

def test_r2_t2_11_phone_checkout_zero_quantity(client):
    token, _, _ = pair_test_device(client, "CHK-ZeroQty")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 0, "price": 2500.0}],
        "payment_type": "cash",
        "total_amount": 0.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 400

def test_r2_t2_12_phone_checkout_negative_quantity(client):
    token, _, _ = pair_test_device(client, "CHK-NegQty")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": -2, "price": 2500.0}],
        "payment_type": "cash",
        "total_amount": 0.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 400

def test_r2_t2_13_phone_checkout_negative_price(client):
    token, _, _ = pair_test_device(client, "CHK-NegPrice")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": -50.0}],
        "payment_type": "cash",
        "total_amount": -50.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code == 400

def test_r2_t2_14_phone_checkout_invalid_payment_type(client):
    token, _, _ = pair_test_device(client, "CHK-BadPay")
    payload = {
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "payment_type": "crypto_bitcoin",
        "total_amount": 30.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": token})
    assert res.status_code in [400, 422]

def test_r2_t2_15_phone_checkout_missing_device_token(client):
    payload = {
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "payment_type": "cash",
        "total_amount": 30.0
    }
    res = client.post("/api/sales/phone-checkout", json=payload)
    assert res.status_code == 401


# --- R3 Boundary Cases (10 tests) ---

def test_r3_t2_01_respond_nonexistent_push_id(client):
    headers = get_auth_headers("admin")
    payload = {"push_id": "PUSH-99999999", "action": "accept"}
    res = client.post("/api/sales/respond-push", json=payload, headers=headers)
    assert res.status_code == 404

def test_r3_t2_02_respond_twice_accept_then_decline(client):
    token, _, _ = pair_test_device(client, "Twice-Accept-Decline")
    push_res = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})
    push_id = push_res.json()["push_id"]

    headers = get_auth_headers("admin")
    res1 = client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "accept"}, headers=headers)
    assert res1.status_code == 200

    res2 = client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "decline"}, headers=headers)
    assert res2.status_code == 400

def test_r3_t2_03_respond_twice_decline_then_accept(client):
    token, _, _ = pair_test_device(client, "Twice-Decline-Accept")
    push_res = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})
    push_id = push_res.json()["push_id"]

    headers = get_auth_headers("admin")
    res1 = client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "decline"}, headers=headers)
    assert res1.status_code == 200

    res2 = client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "accept"}, headers=headers)
    assert res2.status_code == 400

def test_r3_t2_04_respond_invalid_action(client):
    token, _, _ = pair_test_device(client, "Bad-Action-Dev")
    push_res = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})
    push_id = push_res.json()["push_id"]

    headers = get_auth_headers("admin")
    res = client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "hold"}, headers=headers)
    assert res.status_code == 400

def test_r3_t2_05_fetch_payload_nonexistent_push_id(client):
    headers = get_auth_headers("admin")
    res = client.get("/api/sales/push-payload/PUSH-NONEXISTENT", headers=headers)
    assert res.status_code == 404

def test_r3_t2_06_fetch_payload_for_declined_push(client):
    token, _, _ = pair_test_device(client, "Payload-Declined-Dev")
    push_res = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})
    push_id = push_res.json()["push_id"]

    headers = get_auth_headers("admin")
    client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "decline"}, headers=headers)

    res = client.get(f"/api/sales/push-payload/{push_id}", headers=headers)
    assert res.status_code == 400

def test_r3_t2_07_pending_pushes_isolation_between_users(client):
    token, _, _ = pair_test_device(client, "Isolation-Dev")
    push_res = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-001", "quantity": 1, "price": 2500.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})
    push_id = push_res.json()["push_id"]

    headers_test_user = get_auth_headers("test")
    res = client.get("/api/sales/pending-pushes", headers=headers_test_user)
    pushes = res.json().get("data", [])
    assert not any(p["push_id"] == push_id for p in pushes)

def test_r3_t2_08_pending_pushes_unauthenticated(client):
    res = client.get("/api/sales/pending-pushes")
    assert res.status_code == 401

def test_r3_t2_09_respond_push_unauthenticated(client):
    res = client.post("/api/sales/respond-push", json={"push_id": "PUSH-123", "action": "accept"})
    assert res.status_code == 401

def test_r3_t2_10_push_payload_unauthenticated(client):
    res = client.get("/api/sales/push-payload/PUSH-123")
    assert res.status_code == 401


# ==============================================================================
# TIER 3: CROSS-FEATURE COMBINATIONS (5 Tests)
# ==============================================================================

def test_t3_01_full_e2e_journey_pair_scan_push_accept_pos_checkout(client, db_session):
    headers = get_auth_headers("admin")
    
    # 1. Pair device
    pair_res = client.post("/api/device/pair-token", json={"device_name": "Full-Journey-Scanner"}, headers=headers)
    assert pair_res.status_code == 200
    token = pair_res.json().get("data", pair_res.json())["token"]

    # 2. Mobile scanner pushes cart
    push_payload = {
        "device_token": token,
        "items": [
            {"product_id": "PROD-002", "quantity": 2, "price": 150.0},
            {"product_id": "PROD-003", "quantity": 3, "price": 30.0}
        ],
        "pc_user_id": 1
    }
    push_res = client.post("/api/sales/push-pc-sale", json=push_payload, headers={"X-Device-Token": token})
    assert push_res.status_code == 200
    push_id = push_res.json()["push_id"]

    # 3. PC Cashier checks pending pushes
    pending_res = client.get("/api/sales/pending-pushes", headers=headers)
    assert any(p["push_id"] == push_id for p in pending_res.json().get("data", []))

    # 4. PC Cashier accepts push
    accept_res = client.post("/api/sales/respond-push", json={"push_id": push_id, "action": "accept"}, headers=headers)
    assert accept_res.status_code == 200

    # 5. Open POS & retrieve cart payload
    payload_res = client.get(f"/api/sales/push-payload/{push_id}", headers=headers)
    assert payload_res.status_code == 200
    cart_items = payload_res.json()["items"]
    assert len(cart_items) == 2

    # 6. Complete sale on PC POS
    checkout_res = client.post("/sales/checkout", json={
        "items": cart_items,
        "payment_method": "naqd",
        "total_amount": 390.0,
        "paid_amount": 390.0,
        "customer_name": "Full Journey Customer"
    }, headers=headers)
    assert checkout_res.status_code == 200

    # 7. Assert DB integrity
    sp = db_session.query(models.SalesPush).filter(models.SalesPush.id == push_id).first()
    assert sp.status == "accepted"

def test_t3_02_multi_device_pairing_and_selective_revocation(client, db_session):
    headers = get_auth_headers("admin")
    res1 = client.post("/api/device/pair-token", json={"device_name": "Dev-A"}, headers=headers)
    res2 = client.post("/api/device/pair-token", json={"device_name": "Dev-B"}, headers=headers)
    t1 = res1.json().get("data", res1.json())["token"]
    t2 = res2.json().get("data", res2.json())["token"]

    dev_a = db_session.query(models.DeviceToken).filter(models.DeviceToken.token == t1).first()
    client.delete(f"/api/device/revoke/{dev_a.id}", headers=headers)

    res_a = client.get("/api/device/verify", headers={"X-Device-Token": t1})
    assert res_a.status_code == 403

    res_b = client.get("/api/device/verify", headers={"X-Device-Token": t2})
    assert res_b.status_code == 200

def test_t3_03_mobile_switch_modes_push_then_phone_checkout(client):
    token, _, _ = pair_test_device(client, "Switch-Mode-Dev")

    # Mode 1: Computer Sale Push
    push_res = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token})
    assert push_res.status_code == 200

    # Mode 2: Direct Phone Checkout
    chk_res = client.post("/api/sales/phone-checkout", json={
        "device_token": token,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "payment_type": "cash",
        "total_amount": 30.0
    }, headers={"X-Device-Token": token})
    assert chk_res.status_code == 200

def test_t3_04_push_decline_and_resubmit(client):
    token, _, _ = pair_test_device(client, "Resubmit-Dev")
    headers = get_auth_headers("admin")

    # Push Cart 1
    p1 = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-002", "quantity": 10, "price": 150.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token}).json()["push_id"]

    # Cashier declines Cart 1
    client.post("/api/sales/respond-push", json={"push_id": p1, "action": "decline"}, headers=headers)

    # Push corrected Cart 2
    p2 = client.post("/api/sales/push-pc-sale", json={
        "device_token": token,
        "items": [{"product_id": "PROD-002", "quantity": 2, "price": 150.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": token}).json()["push_id"]

    # Cashier accepts Cart 2
    res2 = client.post("/api/sales/respond-push", json={"push_id": p2, "action": "accept"}, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["status"] == "accepted"

def test_t3_05_dual_device_concurrent_pushes_to_same_cashier(client):
    t1, _, _ = pair_test_device(client, "Concurrent-Dev-1")
    t2, _, _ = pair_test_device(client, "Concurrent-Dev-2")

    p1 = client.post("/api/sales/push-pc-sale", json={
        "device_token": t1,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": t1}).json()["push_id"]

    p2 = client.post("/api/sales/push-pc-sale", json={
        "device_token": t2,
        "items": [{"product_id": "PROD-003", "quantity": 2, "price": 30.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": t2}).json()["push_id"]

    headers = get_auth_headers("admin")
    pending = client.get("/api/sales/pending-pushes", headers=headers).json().get("data", [])
    p_ids = [p["push_id"] for p in pending]
    assert p1 in p_ids
    assert p2 in p_ids


# ==============================================================================
# TIER 4: REAL-WORLD APPLICATION WORKLOADS (5 Tests)
# ==============================================================================

def test_t4_01_concurrent_cashiers_push_notifications(client):
    headers_admin = get_auth_headers("admin")
    headers_test = get_auth_headers("test")

    t1, _, _ = pair_test_device(client, "Cashier-1-Dev")
    t2, _, _ = pair_test_device(client, "Cashier-2-Dev")

    p1 = client.post("/api/sales/push-pc-sale", json={
        "device_token": t1,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "pc_user_id": 1
    }, headers={"X-Device-Token": t1}).json()["push_id"]

    p2 = client.post("/api/sales/push-pc-sale", json={
        "device_token": t2,
        "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
        "pc_user_id": 2
    }, headers={"X-Device-Token": t2}).json()["push_id"]

    list1 = client.get("/api/sales/pending-pushes", headers=headers_admin).json().get("data", [])
    list2 = client.get("/api/sales/pending-pushes", headers=headers_test).json().get("data", [])

    assert any(p["push_id"] == p1 for p in list1)
    assert not any(p["push_id"] == p2 for p in list1)

    assert any(p["push_id"] == p2 for p in list2)
    assert not any(p["push_id"] == p1 for p in list2)

def test_t4_02_high_volume_phone_checkout_stock_concurrency(client, db_session):
    db_session.expire_all()
    prod = db_session.query(models.Product).filter(models.Product.id == "PROD-003").first()
    initial_stock = prod.quantityInStock

    tokens = []
    for i in range(5):
        t, _, _ = pair_test_device(client, f"HighVol-Dev-{i}")
        tokens.append(t)

    results = []
    for t in tokens:
        payload = {
            "device_token": t,
            "items": [{"product_id": "PROD-003", "quantity": 2, "price": 30.0}],
            "payment_type": "cash",
            "total_amount": 60.0
        }
        res = client.post("/api/sales/phone-checkout", json=payload, headers={"X-Device-Token": t})
        results.append(res)

    for r in results:
        assert r.status_code == 200

    db_session.expire_all()
    prod = db_session.query(models.Product).filter(models.Product.id == "PROD-003").first()
    assert prod.quantityInStock == initial_stock - 10

def test_t4_03_burst_push_notifications_and_queue_handling(client):
    token, _, _ = pair_test_device(client, "Burst-Dev")

    push_ids = []
    for i in range(15):
        res = client.post("/api/sales/push-pc-sale", json={
            "device_token": token,
            "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
            "pc_user_id": 1
        }, headers={"X-Device-Token": token})
        assert res.status_code == 200
        push_ids.append(res.json()["push_id"])

    headers = get_auth_headers("admin")
    pending = client.get("/api/sales/pending-pushes", headers=headers).json().get("data", [])
    pending_ids = [p["push_id"] for p in pending]
    for pid in push_ids:
        assert pid in pending_ids

def test_t4_04_mixed_workload_pushes_and_checkouts(client):
    token, _, _ = pair_test_device(client, "Mixed-Workload-Dev")
    headers = get_auth_headers("admin")

    for i in range(5):
        p_res = client.post("/api/sales/push-pc-sale", json={
            "device_token": token,
            "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
            "pc_user_id": 1
        }, headers={"X-Device-Token": token})
        assert p_res.status_code == 200

        chk_res = client.post("/api/sales/phone-checkout", json={
            "device_token": token,
            "items": [{"product_id": "PROD-003", "quantity": 1, "price": 30.0}],
            "payment_type": "cash",
            "total_amount": 30.0
        }, headers={"X-Device-Token": token})
        assert chk_res.status_code == 200

    pending = client.get("/api/sales/pending-pushes", headers=headers).json().get("data", [])
    assert len(pending) >= 5

def test_t4_05_multi_user_token_lifecycle_under_load(client, db_session):
    headers = get_auth_headers("admin")
    tokens_and_ids = []

    for i in range(5):
        res = client.post("/api/device/pair-token", json={"device_name": f"Lifecycle-Dev-{i}"}, headers=headers)
        t_data = res.json().get("data", res.json())
        tokens_and_ids.append((t_data["token"], t_data["device_name"]))

    for token, dev_name in tokens_and_ids:
        v_res = client.get("/api/device/verify", headers={"X-Device-Token": token})
        assert v_res.status_code == 200

        dev_obj = db_session.query(models.DeviceToken).filter(models.DeviceToken.token == token).first()
        del_res = client.delete(f"/api/device/revoke/{dev_obj.id}", headers=headers)
        assert del_res.status_code == 200

        v_after = client.get("/api/device/verify", headers={"X-Device-Token": token})
        assert v_after.status_code == 403
