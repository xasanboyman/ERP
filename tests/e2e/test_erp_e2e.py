import pytest
import requests
import random
import time

BASE_URL = "http://127.0.0.1:8000"

# ----------------- HELPERS -----------------
def generate_unique_str():
    return f"{random.randint(100000, 999999)}"

@pytest.fixture(scope="session", autouse=True)
def setup_stages_and_processes():
    # Ensure a basic stage and process are created for E2E tests
    requests.post(f"{BASE_URL}/cutting/stage/save", json={
        "id": "STAGE-001",
        "name": "Cutting Stage 1",
        "price": 10.0,
        "duration": 100
    })
    requests.post(f"{BASE_URL}/cutting/process/save", json={
        "id": "PROC-001",
        "name": "Process 1",
        "stages": [{"id": "STAGE-001", "name": "Cutting Stage 1"}]
    })

# ----------------- TIER 1: FEATURE COVERAGE (25 TESTS) -----------------

# Feature 1: User / Auth Module (5 Tests)
def test_login_success():
    res = requests.post(f"{BASE_URL}/user/login", json={"username": "admin", "password": "admin"})
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert data["data"]["username"] == "admin"
    assert "role" in data["data"]

def test_logout_success():
    res = requests.get(f"{BASE_URL}/user/loginOut")
    assert res.status_code == 200
    assert res.json()["code"] == 0

def test_fetch_user_list_all():
    res = requests.get(f"{BASE_URL}/user/list")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert "list" in data["data"]
    assert len(data["data"]["list"]) > 0

def test_fetch_user_list_filter():
    res = requests.get(f"{BASE_URL}/user/list", params={"username": "admin"})
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    for u in data["data"]["list"]:
        assert "admin" in u["username"].lower()

def test_check_user_role_admin():
    res = requests.post(f"{BASE_URL}/user/login", json={"username": "admin", "password": "admin"})
    assert res.json()["data"]["role"] == "admin"


# Feature 2: Cutting Orders Module (5 Tests)
def test_create_cutting_order():
    order_num = f"ORD-{generate_unique_str()}"
    payload = {
        "order_number": order_num,
        "project": "E2E Project",
        "order_name": "Test Order",
        "responsible_user_ids": ["admin", "test"],
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 100,
                "category": "Software"
            }
        ]
    }
    res = requests.post(f"{BASE_URL}/cutting/order/save", json=payload)
    assert res.status_code == 200
    assert res.json()["code"] == 0

def test_list_cutting_orders():
    res = requests.get(f"{BASE_URL}/cutting/order/list")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert len(data["data"]["list"]) > 0

def test_verify_responsible_users_json():
    order_num = f"ORD-{generate_unique_str()}"
    payload = {
        "order_number": order_num,
        "responsible_user_ids": ["admin", "test"],
        "items": [{"productId": "PROD-001", "quantity": 50}]
    }
    requests.post(f"{BASE_URL}/cutting/order/save", json=payload)
    
    res = requests.get(f"{BASE_URL}/cutting/order/list")
    orders = res.json()["data"]["list"]
    found = [o for o in orders if o["order_number"] == order_num]
    assert len(found) == 1
    assert found[0]["responsible_user_ids"] == ["admin", "test"]

def test_delete_cutting_order():
    order_num = f"ORD-{generate_unique_str()}"
    payload = {
        "order_number": order_num,
        "items": [{"productId": "PROD-001", "quantity": 10}]
    }
    requests.post(f"{BASE_URL}/cutting/order/save", json=payload)
    
    # get id
    res_list = requests.get(f"{BASE_URL}/cutting/order/list")
    orders = res_list.json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]
    
    # delete
    res_del = requests.post(f"{BASE_URL}/cutting/order/delete", json={"ids": [order_id]})
    assert res_del.status_code == 200
    assert res_del.json()["code"] == 0

def test_start_production_success():
    order_num = f"ORD-{generate_unique_str()}"
    payload = {
        "order_number": order_num,
        "items": [{"productId": "PROD-001", "quantity": 10}]
    }
    requests.post(f"{BASE_URL}/cutting/order/save", json=payload)
    
    res_list = requests.get(f"{BASE_URL}/cutting/order/list")
    orders = res_list.json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]
    
    # start production
    res_start = requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
    assert res_start.status_code == 200
    assert res_start.json()["code"] == 0


# Feature 3: Worker Module (5 Tests)
def test_create_worker():
    acc = f"worker_{generate_unique_str()}"
    payload = {
        "name": "E2E Worker",
        "account": acc,
        "baseSalary": 5000.0
    }
    res = requests.post(f"{BASE_URL}/worker/save", json=payload)
    assert res.status_code == 200
    assert res.json()["code"] == 0

def test_update_worker():
    acc = f"worker_{generate_unique_str()}"
    payload = {
        "name": "E2E Worker",
        "account": acc,
        "baseSalary": 5000.0
    }
    requests.post(f"{BASE_URL}/worker/save", json=payload)
    
    # get id with filter to avoid pagination issues
    workers = requests.get(f"{BASE_URL}/worker/list", params={"name": acc}).json()["data"]["list"]
    worker_id = [w["id"] for w in workers if w["account"] == acc][0]
    
    # update
    payload_update = {
        "id": worker_id,
        "name": "Updated Worker Name",
        "account": acc,
        "baseSalary": 6000.0
    }
    res_update = requests.post(f"{BASE_URL}/worker/save", json=payload_update)
    assert res_update.status_code == 200
    assert res_update.json()["code"] == 0

def test_list_workers():
    res = requests.get(f"{BASE_URL}/worker/list")
    assert res.status_code == 200
    assert res.json()["code"] == 0
    assert len(res.json()["data"]["list"]) > 0

def test_generate_unique_employee_code():
    acc = f"worker_{generate_unique_str()}"
    payload = {
        "name": "E2E Worker Unique",
        "account": acc,
        "baseSalary": 5000.0
    }
    requests.post(f"{BASE_URL}/worker/save", json=payload)
    
    workers = requests.get(f"{BASE_URL}/worker/list", params={"name": acc}).json()["data"]["list"]
    worker = [w for w in workers if w["account"] == acc][0]
    
    assert "employee_code" in worker
    assert worker["employee_code"] is not None
    assert len(worker["employee_code"]) == 6
    assert worker["employee_code"].isdigit()

def test_delete_worker():
    acc = f"worker_{generate_unique_str()}"
    payload = {
        "name": "E2E Worker Del",
        "account": acc,
        "baseSalary": 5000.0
    }
    requests.post(f"{BASE_URL}/worker/save", json=payload)
    
    workers = requests.get(f"{BASE_URL}/worker/list", params={"name": acc}).json()["data"]["list"]
    worker_id = [w["id"] for w in workers if w["account"] == acc][0]
    
    res_del = requests.post(f"{BASE_URL}/worker/delete", json={"ids": [worker_id]})
    assert res_del.status_code == 200
    assert res_del.json()["code"] == 0


# Feature 4: Product Module (5 Tests)
def test_create_product():
    sku = f"SKU-{generate_unique_str()}"
    payload = {
        "productName": "E2E Product",
        "SKU": sku,
        "category": "Electronics",
        "price": 100.0,
        "cost": 50.0,
        "quantityInStock": 10
    }
    res = requests.post(f"{BASE_URL}/product/save", json=payload)
    assert res.status_code == 200
    assert res.json()["code"] == 0

def test_update_product():
    sku = f"SKU-{generate_unique_str()}"
    payload = {
        "productName": "E2E Product Update",
        "SKU": sku,
        "category": "Electronics",
        "price": 100.0,
        "cost": 50.0,
        "quantityInStock": 10
    }
    requests.post(f"{BASE_URL}/product/save", json=payload)
    
    # get id with filter
    products = requests.get(f"{BASE_URL}/product/list", params={"productName": sku}).json()["data"]["list"]
    prod_id = [p["id"] for p in products if p["SKU"] == sku][0]
    
    # update
    payload_update = {
        "id": prod_id,
        "productName": "Updated SKU Product",
        "SKU": sku,
        "category": "Electronics",
        "price": 120.0,
        "cost": 60.0,
        "quantityInStock": 15
    }
    res_update = requests.post(f"{BASE_URL}/product/save", json=payload_update)
    assert res_update.status_code == 200
    assert res_update.json()["code"] == 0

def test_list_products():
    res = requests.get(f"{BASE_URL}/product/list")
    assert res.status_code == 200
    assert res.json()["code"] == 0
    assert len(res.json()["data"]["list"]) > 0

def test_get_product_detail():
    sku = f"SKU-{generate_unique_str()}"
    payload = {
        "productName": "E2E Product Detail",
        "SKU": sku,
        "category": "Electronics",
        "price": 10.0,
        "cost": 5.0,
        "quantityInStock": 1
    }
    requests.post(f"{BASE_URL}/product/save", json=payload)
    
    products = requests.get(f"{BASE_URL}/product/list", params={"productName": sku}).json()["data"]["list"]
    prod_id = [p["id"] for p in products if p["SKU"] == sku][0]
    
    res = requests.get(f"{BASE_URL}/product/detail", params={"id": prod_id})
    assert res.status_code == 200
    assert res.json()["code"] == 0
    assert res.json()["data"]["productName"] == "E2E Product Detail"

def test_delete_product():
    sku = f"SKU-{generate_unique_str()}"
    payload = {
        "productName": "E2E Product Del",
        "SKU": sku,
        "category": "Electronics",
        "price": 100.0,
        "cost": 50.0,
        "quantityInStock": 10
    }
    requests.post(f"{BASE_URL}/product/save", json=payload)
    
    products = requests.get(f"{BASE_URL}/product/list", params={"productName": sku}).json()["data"]["list"]
    prod_id = [p["id"] for p in products if p["SKU"] == sku][0]
    
    res_del = requests.post(f"{BASE_URL}/product/delete", json={"ids": [prod_id]})
    assert res_del.status_code == 200
    assert res_del.json()["code"] == 0


# Feature 5: QR Code Module (5 Tests)
def test_generate_qr_code_ulid():
    order_num = f"ORD-{generate_unique_str()}"
    payload = {
        "order_number": order_num,
        "items": [{"productId": "PROD-001", "quantity": 10, "cuttingProcessId": "PROC-001"}]
    }
    requests.post(f"{BASE_URL}/cutting/order/save", json=payload)
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]
    requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
    
    tasks = requests.get(f"{BASE_URL}/cutting/task/list").json()["data"]["list"]
    task_id = [t["id"] for t in tasks if t["orderId"] == order_id][0]
    
    res_qr = requests.post(f"{BASE_URL}/qr/save", json={"taskId": task_id, "quantity": 5})
    assert res_qr.status_code == 200
    qr_code = res_qr.json()["data"]
    assert len(qr_code) == 26  # ULID format length
    assert qr_code.isalnum()

def test_list_qr_codes():
    res = requests.get(f"{BASE_URL}/qr/list")
    assert res.status_code == 200
    assert res.json()["code"] == 0
    assert len(res.json()["data"]["list"]) > 0

def test_qr_code_metadata():
    res = requests.get(f"{BASE_URL}/qr/list")
    codes = res.json()["data"]["list"]
    assert len(codes) > 0
    q = codes[-1]
    assert "taskId" in q
    assert "quantity" in q
    assert "status" in q
    assert "workerId" in q

def test_assign_worker_to_qr():
    # Setup worker
    acc = f"worker_{generate_unique_str()}"
    requests.post(f"{BASE_URL}/worker/save", json={"name": "Scan Worker", "account": acc})
    workers = requests.get(f"{BASE_URL}/worker/list", params={"name": acc}).json()["data"]["list"]
    worker_id = [w["id"] for w in workers if w["account"] == acc][0]
    
    # Setup QR Code
    res = requests.get(f"{BASE_URL}/qr/list")
    qr_id = res.json()["data"]["list"][-1]["id"]
    
    # Assign
    res_assign = requests.post(f"{BASE_URL}/qr/assign-worker", json={"qrId": qr_id, "workerId": worker_id})
    assert res_assign.status_code == 200
    assert res_assign.json()["code"] == 0
    
    # Verify assignment
    res_verify = requests.get(f"{BASE_URL}/qr/list")
    q = [item for item in res_verify.json()["data"]["list"] if item["id"] == qr_id][0]
    assert q["workerId"] == worker_id
    assert q["status"] == "scanned"

def test_update_qr_status():
    res = requests.get(f"{BASE_URL}/qr/list")
    qr_id = res.json()["data"]["list"][-1]["id"]
    
    res_up = requests.post(f"{BASE_URL}/qr/update-status", json={"qrId": qr_id, "status": "processing"})
    assert res_up.status_code == 200
    assert res_up.json()["code"] == 0
    
    res_verify = requests.get(f"{BASE_URL}/qr/list")
    q = [item for item in res_verify.json()["data"]["list"] if item["id"] == qr_id][0]
    assert q["status"] == "processing"


# ----------------- TIER 2: BOUNDARY & CORNER CASES (25 TESTS) -----------------

# Feature 1: User / Auth Module (5 Tests)
def test_login_invalid_password():
    res = requests.post(f"{BASE_URL}/user/login", json={"username": "admin", "password": "wrongpassword"})
    assert res.json()["code"] != 0

def test_login_nonexistent_user():
    res = requests.post(f"{BASE_URL}/user/login", json={"username": "no_such_user", "password": "any"})
    assert res.json()["code"] != 0

def test_user_list_invalid_page():
    res = requests.get(f"{BASE_URL}/user/list", params={"pageIndex": 9999})
    assert res.json()["code"] == 0
    assert len(res.json()["data"]["list"]) == 0

def test_user_list_negative_page_size():
    res = requests.get(f"{BASE_URL}/user/list", params={"pageSize": -5})
    assert res.status_code == 200

def test_login_empty_payload():
    res = requests.post(f"{BASE_URL}/user/login", json={})
    assert res.status_code == 422


# Feature 2: Cutting Orders Module (5 Tests)
def test_create_order_empty_items():
    order_num = f"ORD-EMPTY-{generate_unique_str()}"
    res = requests.post(f"{BASE_URL}/cutting/order/save", json={"order_number": order_num, "items": []})
    assert res.status_code in [200, 422]

def test_create_order_duplicate_number():
    order_num = f"ORD-{generate_unique_str()}"
    payload = {"order_number": order_num, "items": [{"productId": "PROD-001", "quantity": 1}]}
    requests.post(f"{BASE_URL}/cutting/order/save", json=payload)
    res = requests.post(f"{BASE_URL}/cutting/order/save", json=payload)
    assert res.status_code in [500, 400] or res.json()["code"] != 0

def test_start_production_nonexistent_order():
    res = requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": "nonexistent"})
    assert res.json()["code"] == 404

def test_delete_order_nonexistent():
    res = requests.post(f"{BASE_URL}/cutting/order/delete", json={"ids": ["nonexistent_id"]})
    assert res.status_code == 200

def test_create_order_missing_fields():
    res = requests.post(f"{BASE_URL}/cutting/order/save", json={"project": "No Order Number"})
    assert res.status_code == 422


# Feature 3: Worker Module (5 Tests)
def test_create_worker_duplicate_account():
    acc = f"worker_{generate_unique_str()}"
    payload = {"name": "Worker 1", "account": acc}
    requests.post(f"{BASE_URL}/worker/save", json=payload)
    
    res = requests.post(f"{BASE_URL}/worker/save", json={"name": "Worker 2", "account": acc})
    assert res.status_code in [500, 400] or res.json()["code"] != 0

def test_create_worker_invalid_email():
    payload = {"name": "Worker", "account": f"worker_{generate_unique_str()}", "email": "invalid-email"}
    res = requests.post(f"{BASE_URL}/worker/save", json=payload)
    assert res.status_code in [200, 422]

def test_update_worker_nonexistent():
    payload = {"id": "W-NONEXISTENT", "name": "No Worker", "account": f"worker_{generate_unique_str()}"}
    res = requests.post(f"{BASE_URL}/worker/save", json=payload)
    assert res.status_code == 200

def test_delete_worker_missing_ids():
    res = requests.post(f"{BASE_URL}/worker/delete", json={})
    assert res.status_code == 500 or res.json()["code"] != 0

def test_create_worker_missing_required_fields():
    res = requests.post(f"{BASE_URL}/worker/save", json={"name": "No Account Worker"})
    assert res.status_code == 422


# Feature 4: Product Module (5 Tests)
def test_create_product_duplicate_sku():
    sku = f"SKU-{generate_unique_str()}"
    payload = {"productName": "P1", "SKU": sku, "category": "A", "price": 10.0, "cost": 5.0, "quantityInStock": 1}
    requests.post(f"{BASE_URL}/product/save", json=payload)
    
    res = requests.post(f"{BASE_URL}/product/save", json=payload)
    assert res.status_code in [500, 400] or res.json()["code"] != 0

def test_create_product_negative_price():
    sku = f"SKU-{generate_unique_str()}"
    payload = {"productName": "P", "SKU": sku, "category": "A", "price": -10.0, "cost": 5.0, "quantityInStock": 1}
    res = requests.post(f"{BASE_URL}/product/save", json=payload)
    assert res.status_code in [200, 422]

def test_create_product_negative_cost():
    sku = f"SKU-{generate_unique_str()}"
    payload = {"productName": "P", "SKU": sku, "category": "A", "price": 10.0, "cost": -5.0, "quantityInStock": 1}
    res = requests.post(f"{BASE_URL}/product/save", json=payload)
    assert res.status_code in [200, 422]

def test_delete_product_nonexistent():
    res = requests.post(f"{BASE_URL}/product/delete", json={"ids": ["nonexistent_sku"]})
    assert res.status_code == 200

def test_product_detail_nonexistent():
    res = requests.get(f"{BASE_URL}/product/detail", params={"id": "PROD-NONEXISTENT"})
    assert res.status_code == 200
    assert res.json()["code"] == 404


# Feature 5: QR Code Module (5 Tests)
def test_generate_qr_nonexistent_task():
    res = requests.post(f"{BASE_URL}/qr/save", json={"taskId": "nonexistent_task", "quantity": 1})
    assert res.status_code in [500, 400, 404] or res.json()["code"] != 0

def test_assign_qr_nonexistent_worker():
    res = requests.get(f"{BASE_URL}/qr/list")
    qr_id = res.json()["data"]["list"][-1]["id"]
    res_assign = requests.post(f"{BASE_URL}/qr/assign-worker", json={"qrId": qr_id, "workerId": "nonexistent_worker"})
    assert res_assign.json()["code"] == 404

def test_assign_nonexistent_qr():
    acc = f"worker_{generate_unique_str()}"
    requests.post(f"{BASE_URL}/worker/save", json={"name": "Scan Worker", "account": acc})
    workers = requests.get(f"{BASE_URL}/worker/list", params={"name": acc}).json()["data"]["list"]
    worker_id = [w["id"] for w in workers if w["account"] == acc][0]
    
    res = requests.post(f"{BASE_URL}/qr/assign-worker", json={"qrId": "nonexistent_qr", "workerId": worker_id})
    assert res.json()["code"] == 404

def test_update_status_nonexistent_qr():
    res = requests.post(f"{BASE_URL}/qr/update-status", json={"qrId": "nonexistent_qr", "status": "completed"})
    assert res.json()["code"] == 404

def test_update_status_empty_status():
    res = requests.get(f"{BASE_URL}/qr/list")
    qr_id = res.json()["data"]["list"][-1]["id"]
    res_up = requests.post(f"{BASE_URL}/qr/update-status", json={"qrId": qr_id})
    assert res_up.status_code == 500 or res_up.json()["code"] != 0


# ----------------- TIER 3: CROSS-FEATURE COMBINATIONS (5 TESTS) -----------------

def test_pairwise_product_and_cutting_order():
    sku = f"SKU-{generate_unique_str()}"
    prod_payload = {"productName": "Cross Product", "SKU": sku, "category": "Pairwise", "price": 100.0, "cost": 50.0, "quantityInStock": 10}
    requests.post(f"{BASE_URL}/product/save", json=prod_payload)
    
    products = requests.get(f"{BASE_URL}/product/list", params={"productName": sku}).json()["data"]["list"]
    prod_id = [p["id"] for p in products if p["SKU"] == sku][0]
    
    order_num = f"ORD-{generate_unique_str()}"
    order_payload = {
        "order_number": order_num,
        "items": [{"productId": prod_id, "quantity": 25}]
    }
    res_order = requests.post(f"{BASE_URL}/cutting/order/save", json=order_payload)
    assert res_order.json()["code"] == 0

def test_pairwise_user_and_cutting_order():
    users = requests.get(f"{BASE_URL}/user/list").json()["data"]["list"]
    usernames = [u["username"] for u in users[:2]]
    
    order_num = f"ORD-{generate_unique_str()}"
    order_payload = {
        "order_number": order_num,
        "responsible_user_ids": usernames,
        "items": [{"productId": "PROD-001", "quantity": 10}]
    }
    requests.post(f"{BASE_URL}/cutting/order/save", json=order_payload)
    
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    found = [o for o in orders if o["order_number"] == order_num][0]
    assert found["responsible_user_ids"] == usernames

def test_pairwise_cutting_task_and_qr_code():
    order_num = f"ORD-{generate_unique_str()}"
    order_payload = {
        "order_number": order_num,
        "items": [{"productId": "PROD-001", "quantity": 10, "cuttingProcessId": "PROC-001"}]
    }
    requests.post(f"{BASE_URL}/cutting/order/save", json=order_payload)
    
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]
    
    requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
    
    tasks = requests.get(f"{BASE_URL}/cutting/task/list").json()["data"]["list"]
    task_id = [t["id"] for t in tasks if t["orderId"] == order_id][0]
    
    res_qr = requests.post(f"{BASE_URL}/qr/save", json={"taskId": task_id, "quantity": 10})
    assert res_qr.json()["code"] == 0

def test_pairwise_qr_code_and_worker():
    acc = f"worker_{generate_unique_str()}"
    requests.post(f"{BASE_URL}/worker/save", json={"name": "Pairwise Worker", "account": acc})
    workers = requests.get(f"{BASE_URL}/worker/list", params={"name": acc}).json()["data"]["list"]
    worker_id = [w["id"] for w in workers if w["account"] == acc][0]
    
    # Generate QR Code (create an order first to make sure tasks exist)
    order_num = f"ORD-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/cutting/order/save", json={
        "order_number": order_num, "items": [{"productId": "PROD-001", "quantity": 10, "cuttingProcessId": "PROC-001"}]
    })
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]
    requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
    
    tasks = requests.get(f"{BASE_URL}/cutting/task/list").json()["data"]["list"]
    task_id = [t["id"] for t in tasks if t["orderId"] == order_id][0]
    
    res_qr = requests.post(f"{BASE_URL}/qr/save", json={"taskId": task_id, "quantity": 5})
    qr_code = res_qr.json()["data"]
    
    res_assign = requests.post(f"{BASE_URL}/qr/assign-worker", json={"code": qr_code, "workerId": worker_id})
    assert res_assign.json()["code"] == 0

def test_pairwise_execution_and_salary():
    acc = f"worker_{generate_unique_str()}"
    requests.post(f"{BASE_URL}/worker/save", json={"name": "Execution Worker", "account": acc})
    workers = requests.get(f"{BASE_URL}/worker/list", params={"name": acc}).json()["data"]["list"]
    worker_id = [w["id"] for w in workers if w["account"] == acc][0]
    
    # Make sure task exists
    order_num = f"ORD-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/cutting/order/save", json={
        "order_number": order_num, "items": [{"productId": "PROD-001", "quantity": 10, "cuttingProcessId": "PROC-001"}]
    })
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]
    requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
    
    tasks = requests.get(f"{BASE_URL}/cutting/task/list").json()["data"]["list"]
    task_id = [t["id"] for t in tasks if t["orderId"] == order_id][0]
    
    exec_payload = {"taskId": task_id, "workerId": worker_id, "quantity": 5, "comment": "Pairwise execution"}
    res_exec = requests.post(f"{BASE_URL}/cutting/task/execution/save", json=exec_payload)
    assert res_exec.json()["code"] == 0
    
    sal_payload = {
        "workerId": worker_id,
        "baseSalary": 1000.0,
        "allowance": 100.0,
        "deduction": 50.0,
        "remark": "Pairwise Salary"
    }
    res_sal = requests.post(f"{BASE_URL}/salary/save", json=sal_payload)
    assert res_sal.json()["code"] == 0
    
    res_sal_list = requests.get(f"{BASE_URL}/salary/list", params={"workerId": worker_id})
    salaries = res_sal_list.json()["data"]["list"]
    assert any(s["workerId"] == worker_id for s in salaries)


# ----------------- TIER 4: REAL-WORLD APPLICATION SCENARIOS (5 TESTS) -----------------

def test_workload_1():
    # 1. Product creation
    sku = f"SKU-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/product/save", json={
        "productName": "WL1 Product", "SKU": sku, "category": "WL1", "price": 200.0, "cost": 100.0, "quantityInStock": 100
    })
    products = requests.get(f"{BASE_URL}/product/list", params={"productName": sku}).json()["data"]["list"]
    prod_id = [p["id"] for p in products if p["SKU"] == sku][0]

    # 2. Cutting Order Setup + 3. Assign responsible users
    order_num = f"ORD-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/cutting/order/save", json={
        "order_number": order_num,
        "project": "WL1 Project",
        "order_name": "WL1 Order",
        "responsible_user_ids": ["admin"],
        "items": [{"productId": prod_id, "quantity": 10, "cuttingProcessId": "PROC-001"}]
    })
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]

    # 4. Start Production
    requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
    tasks = requests.get(f"{BASE_URL}/cutting/task/list").json()["data"]["list"]
    task_id = [t["id"] for t in tasks if t["orderId"] == order_id][0]

    # 5. Generate QR
    res_qr = requests.post(f"{BASE_URL}/qr/save", json={"taskId": task_id, "quantity": 10})
    qr_code = res_qr.json()["data"]

    # 6. Scan QR & 7. Assign worker
    acc = f"worker_{generate_unique_str()}"
    requests.post(f"{BASE_URL}/worker/save", json={"name": "WL1 Worker", "account": acc})
    workers = requests.get(f"{BASE_URL}/worker/list", params={"name": acc}).json()["data"]["list"]
    worker_id = [w["id"] for w in workers if w["account"] == acc][0]

    # This auto-executes the task and completes it
    res_assign = requests.post(f"{BASE_URL}/qr/assign-worker", json={"code": qr_code, "workerId": worker_id})
    assert res_assign.json()["code"] == 0

    # 8. Complete production (verifying cascading status)
    order_verify = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    completed_order = [o for o in order_verify if o["id"] == order_id][0]
    assert completed_order["status"] == "completed"

def test_workload_2():
    users = requests.get(f"{BASE_URL}/user/list").json()["data"]["list"]
    usernames = [u["username"] for u in users[:5]]
    
    order_num = f"ORD-{generate_unique_str()}"
    payload = {
        "order_number": order_num,
        "project": "Avatar Parity",
        "responsible_user_ids": usernames,
        "items": [{"productId": "PROD-001", "quantity": 100}]
    }
    res_save = requests.post(f"{BASE_URL}/cutting/order/save", json=payload)
    assert res_save.json()["code"] == 0
    
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    saved_order = [o for o in orders if o["order_number"] == order_num][0]
    assert saved_order["responsible_user_ids"] == usernames

def test_workload_3():
    # 1. Worker onboarding
    acc = f"worker_{generate_unique_str()}"
    requests.post(f"{BASE_URL}/worker/save", json={"name": "Onboarding Worker", "account": acc, "baseSalary": 4000.0})
    
    # 2. Employee code generation
    workers = requests.get(f"{BASE_URL}/worker/list", params={"name": acc}).json()["data"]["list"]
    worker = [w for w in workers if w["account"] == acc][0]
    worker_id = worker["id"]
    emp_code = worker["employee_code"]
    assert len(emp_code) == 6
    
    # 3. QR scan task execution (create an order first to ensure a task exists)
    order_num = f"ORD-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/cutting/order/save", json={
        "order_number": order_num, "items": [{"productId": "PROD-001", "quantity": 10, "cuttingProcessId": "PROC-001"}]
    })
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]
    requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
    
    tasks = requests.get(f"{BASE_URL}/cutting/task/list").json()["data"]["list"]
    task_id = [t["id"] for t in tasks if t["orderId"] == order_id][0]
    
    res_qr = requests.post(f"{BASE_URL}/qr/save", json={"taskId": task_id, "quantity": 8})
    qr_code = res_qr.json()["data"]
    
    res_scan = requests.post(f"{BASE_URL}/qr/assign-worker", json={"code": qr_code, "workerId": worker_id})
    assert res_scan.json()["code"] == 0
    
    # 4. Salary / Payout analytics verification
    requests.post(f"{BASE_URL}/salary/payout", json={"workerIds": [worker_id], "allowance": 200.0, "deduction": 50.0})
    
    # Check salary list
    salaries = requests.get(f"{BASE_URL}/salary/list", params={"workerId": worker_id}).json()["data"]["list"]
    found_salary = [s for s in salaries if s["workerId"] == worker_id][0]
    assert found_salary["baseSalary"] == 4000.0
    assert found_salary["allowance"] == 200.0
    assert found_salary["deduction"] == 50.0
    assert found_salary["netSalary"] == 4150.0

def test_workload_4():
    # 1. Post invalid payload
    res_invalid = requests.post(f"{BASE_URL}/cutting/order/save", json={
        "project": "Recovery Project", "items": [{"productId": "PROD-001", "quantity": 10}]
    })
    assert res_invalid.status_code == 422
    
    # 2. Submit correct payload
    order_num = f"ORD-{generate_unique_str()}"
    payload = {
        "order_number": order_num,
        "project": "Recovery Project",
        "items": [{"productId": "PROD-001", "quantity": 10, "cuttingProcessId": "PROC-001"}]
    }
    res_correct = requests.post(f"{BASE_URL}/cutting/order/save", json=payload)
    assert res_correct.json()["code"] == 0
    
    # 3. Check cascading status
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order = [o for o in orders if o["order_number"] == order_num][0]
    assert order["status"] == "created"
    
    # Start production
    requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order["id"]})
    
    orders_2 = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order_2 = [o for o in orders_2 if o["id"] == order["id"]][0]
    assert order_2["status"] == "in_production"

def test_workload_5():
    sku = f"SKU-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/product/save", json={
        "productName": "Audit Product", "SKU": sku, "category": "Audit", "price": 1.0, "cost": 1.0, "quantityInStock": 1
    })
    
    res_logs = requests.get(f"{BASE_URL}/activity/list")
    logs = res_logs.json()["data"]["list"]
    assert len(logs) > 0
    product_logs = [l for l in logs if l["entity"] == "product" and l["entityName"] == "Audit Product"]
    assert len(product_logs) > 0
    assert product_logs[-1]["action"] in ["created", "updated"]
    
    res_analytics = requests.get(f"{BASE_URL}/analysis/total")
    assert res_analytics.status_code == 200
    assert res_analytics.json()["code"] == 0

def test_v1_status():
    res = requests.get(f"{BASE_URL}/v1/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["version"] == "1.0.0"
    assert "app" in data
    assert "timestamp" in data

def test_v1_qr_scan():
    payload = {"qr_code": "TEST-QR-123456"}
    res = requests.post(f"{BASE_URL}/v1/qr/scan", json=payload)
    assert res.status_code == 501
    data = res.json()
    assert data["success"] is False
    assert "message" in data
    assert "next_step" in data
    assert data["data"]["qr_code"] == "TEST-QR-123456"

def test_department_users_management():
    # 1. Test Listing filtered by department
    res = requests.get(f"{BASE_URL}/department/users", params={"id": "DEPT-RD"})
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    users = data["data"]["list"]
    usernames = [u["username"] for u in users]
    assert "test" in usernames
    assert "test_dept_user" in usernames
    assert "admin" not in usernames

    # 2. Test saving a new user with flat department_id string
    payload_flat = {
        "username": "new_flat_user",
        "email": "flat@example.com",
        "roleId": "2",
        "department": "DEPT-RD"
    }
    res_save = requests.post(f"{BASE_URL}/department/user/save", json=payload_flat)
    assert res_save.status_code == 200
    assert res_save.json()["code"] == 0

    # Verify the user exists and has default password
    res_login = requests.post(f"{BASE_URL}/user/login", json={"username": "new_flat_user", "password": "123456"})
    assert res_login.status_code == 200
    assert res_login.json()["code"] == 0
    
    # Get user ID from department list
    res_list = requests.get(f"{BASE_URL}/department/users", params={"id": "DEPT-RD"})
    new_user_id = next(int(u["id"]) for u in res_list.json()["data"]["list"] if u["username"] == "new_flat_user")

    # 3. Test saving a new user with nested department object
    payload_nested = {
        "username": "new_nested_user",
        "email": "nested@example.com",
        "role": "admin",
        "roleId": "1",
        "department": {"id": "DEPT-HQ", "departmentName": "Bosh Ofis"}
    }
    res_save2 = requests.post(f"{BASE_URL}/department/user/save", json=payload_nested)
    assert res_save2.status_code == 200
    assert res_save2.json()["code"] == 0

    # Verify nested user is created
    res_login2 = requests.post(f"{BASE_URL}/user/login", json={"username": "new_nested_user", "password": "123456"})
    assert res_login2.status_code == 200
    assert res_login2.json()["code"] == 0
    assert res_login2.json()["data"]["role"] == "admin"
    
    # Get user ID from department list
    res_list2 = requests.get(f"{BASE_URL}/department/users", params={"id": "DEPT-HQ"})
    nested_user_id = next(int(u["id"]) for u in res_list2.json()["data"]["list"] if u["username"] == "new_nested_user")

    # Verify department listing for DEPT-HQ includes new_nested_user and admin
    res_hq = requests.get(f"{BASE_URL}/department/users", params={"id": "DEPT-HQ"})
    hq_users = [u["username"] for u in res_hq.json()["data"]["list"]]
    assert "admin" in hq_users
    assert "new_nested_user" in hq_users

    # 4. Test updating an existing user
    payload_update = {
        "id": new_user_id,
        "username": "updated_flat_user",
        "email": "updated_flat@example.com",
        "roleId": "1",
        "department": "DEPT-HQ"
    }
    res_update = requests.post(f"{BASE_URL}/department/user/save", json=payload_update)
    assert res_update.status_code == 200
    assert res_update.json()["code"] == 0

    # Verify update
    res_login_updated = requests.post(f"{BASE_URL}/user/login", json={"username": "updated_flat_user", "password": "123456"})
    assert res_login_updated.status_code == 200
    assert res_login_updated.json()["data"]["role"] == "admin"

    # Verify updated user moved to DEPT-HQ and has updated email
    res_hq_updated = requests.get(f"{BASE_URL}/department/users", params={"id": "DEPT-HQ"})
    hq_users_data = res_hq_updated.json()["data"]["list"]
    hq_users_names = [u["username"] for u in hq_users_data]
    assert "updated_flat_user" in hq_users_names
    updated_user = next(u for u in hq_users_data if u["username"] == "updated_flat_user")
    assert updated_user["email"] == "updated_flat@example.com"

    # 5. Test deleting department users
    res_delete = requests.post(f"{BASE_URL}/department/user/delete", json={"ids": [new_user_id, nested_user_id]})
    assert res_delete.status_code == 200
    assert res_delete.json()["code"] == 0

    # Verify they no longer exist
    res_login_deleted = requests.post(f"{BASE_URL}/user/login", json={"username": "updated_flat_user", "password": "123456"})
    assert res_login_deleted.json()["code"] == 500

    # Seed another user to delete via single string ID
    payload_str_user = {
        "username": "delete_str_user",
        "email": "str_del@example.com",
        "roleId": "2",
        "department": "DEPT-RD"
    }
    requests.post(f"{BASE_URL}/department/user/save", json=payload_str_user)
    
    res_login_str = requests.post(f"{BASE_URL}/user/login", json={"username": "delete_str_user", "password": "123456"})
    assert res_login_str.status_code == 200
    
    res_list_str = requests.get(f"{BASE_URL}/department/users", params={"id": "DEPT-RD"})
    del_str_id = next(int(u["id"]) for u in res_list_str.json()["data"]["list"] if u["username"] == "delete_str_user")
    
    # Delete using single string ID
    res_del_str = requests.post(f"{BASE_URL}/department/user/delete", json={"ids": str(del_str_id)})
    assert res_del_str.status_code == 200
    assert res_del_str.json()["code"] == 0
    
    res_login_str_deleted = requests.post(f"{BASE_URL}/user/login", json={"username": "delete_str_user", "password": "123456"})
    assert res_login_str_deleted.json()["code"] == 500



