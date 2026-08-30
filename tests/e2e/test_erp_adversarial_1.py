import pytest
import requests
import random
import time

BASE_URL = "http://127.0.0.1:8000"

def generate_unique_str():
    return f"{random.randint(100000, 999999)}"

@pytest.fixture(scope="session", autouse=True)
def setup_stages_and_processes():
    # Ensure a basic stage and process are created for E2E tests
    requests.post(f"{BASE_URL}/cutting/stage/save", json={
        "id": "STAGE-ADV",
        "name": "Cutting Stage Adversarial",
        "price": 15.0,
        "duration": 50
    })
    requests.post(f"{BASE_URL}/cutting/process/save", json={
        "id": "PROC-ADV",
        "name": "Process Adversarial",
        "stages": [{"id": "STAGE-ADV", "name": "Cutting Stage Adversarial"}]
    })

# 1. QR Code Replay Attack Vulnerability Test
def test_adversarial_qr_replay():
    # 1. Setup a worker
    acc = f"worker_adv_{generate_unique_str()}"
    res_worker = requests.post(f"{BASE_URL}/worker/save", json={"name": "Adv Worker", "account": acc})
    assert res_worker.status_code == 200
    
    workers = requests.get(f"{BASE_URL}/worker/list", params={"name": acc}).json()["data"]["list"]
    worker_id = [w["id"] for w in workers if w["account"] == acc][0]

    # 2. Setup product
    sku = f"SKU-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/product/save", json={
        "productName": "Adv Product", "SKU": sku, "category": "Adv", "price": 10.0, "cost": 5.0, "quantityInStock": 10
    })
    products = requests.get(f"{BASE_URL}/product/list", params={"productName": sku}).json()["data"]["list"]
    prod_id = [p["id"] for p in products if p["SKU"] == sku][0]

    # 3. Create Cutting Order
    order_num = f"ORD-ADV-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/cutting/order/save", json={
        "order_number": order_num,
        "items": [{"productId": prod_id, "quantity": 10, "cuttingProcessId": "PROC-ADV"}]
    })
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]

    # 4. Start Production to generate tasks
    requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
    tasks = requests.get(f"{BASE_URL}/cutting/task/list").json()["data"]["list"]
    task_id = [t["id"] for t in tasks if t["orderId"] == order_id][0]

    # 5. Generate QR Code
    res_qr = requests.post(f"{BASE_URL}/qr/save", json={"taskId": task_id, "quantity": 5})
    qr_code = res_qr.json()["data"]

    # 6. Assign worker (Scan 1)
    res_scan1 = requests.post(f"{BASE_URL}/qr/assign-worker", json={"code": qr_code, "workerId": worker_id})
    assert res_scan1.json()["code"] == 0

    # 7. Assign worker again (Scan 2 - Replay Attack / Double Scan)
    res_scan2 = requests.post(f"{BASE_URL}/qr/assign-worker", json={"code": qr_code, "workerId": worker_id})
    
    # We expect the system to REJECT double assignment of the same QR code
    # to prevent double task execution / double pay.
    assert res_scan2.json()["code"] != 0, "Security/Business logic failure: Allowed QR replay/double scan!"

    # Also query execution records for this task: there should only be 1 execution record
    executions = requests.get(f"{BASE_URL}/cutting/task/execution/list").json()["data"]["list"]
    task_execs = [e for e in executions if e["taskId"] == task_id]
    assert len(task_execs) == 1, f"Security/Business logic failure: Created {len(task_execs)} executions for single QR!"


# 2. Database Integrity Cascading Delete (Foreign Key) Test
def test_adversarial_deleted_worker_cascades():
    # 1. Setup a worker
    acc = f"worker_adv_{generate_unique_str()}"
    requests.post(f"{BASE_URL}/worker/save", json={"name": "Temp Worker", "account": acc})
    workers = requests.get(f"{BASE_URL}/worker/list", params={"name": acc}).json()["data"]["list"]
    worker_id = [w["id"] for w in workers if w["account"] == acc][0]

    # 2. Create a salary record for this worker
    res_sal = requests.post(f"{BASE_URL}/salary/save", json={
        "workerId": worker_id,
        "baseSalary": 2500.0,
        "allowance": 100.0,
        "deduction": 50.0,
        "status": "pending"
    })
    assert res_sal.status_code == 200

    # 3. Delete the worker
    res_del = requests.post(f"{BASE_URL}/worker/delete", json={"ids": [worker_id]})
    assert res_del.status_code == 200

    # 4. Check if salary record is deleted due to foreign key cascade ON DELETE CASCADE
    salaries = requests.get(f"{BASE_URL}/salary/list", params={"workerId": worker_id}).json()["data"]["list"]
    worker_salaries = [s for s in salaries if s["workerId"] == worker_id]
    
    # We expect either the salary record was cascaded away (deleted), or if it exists, it should be cleaned up.
    # If the salary record still exists and references a deleted worker, database integrity is broken.
    assert len(worker_salaries) == 0, "Database integrity failure: Salary record was NOT deleted when worker was deleted (dangling foreign key)!"


# 3. Database Integrity on Creation with Nonexistent References (FK Check)
def test_adversarial_nonexistent_product_fk():
    order_num = f"ORD-ADV-{generate_unique_str()}"
    payload = {
        "order_number": order_num,
        "items": [{"productId": "NONEXISTENT_PRODUCT_ID", "quantity": 10, "cuttingProcessId": "PROC-ADV"}]
    }
    res = requests.post(f"{BASE_URL}/cutting/order/save", json=payload)
    
    # We expect the creation of an order referencing a nonexistent product to fail
    assert res.status_code in [400, 422] or res.json()["code"] != 0, "Database integrity failure: Allowed order item referencing nonexistent product!"


# 4. Input Validation Boundary Test: Negative Quantities
def test_adversarial_negative_quantity_order():
    order_num = f"ORD-ADV-{generate_unique_str()}"
    payload = {
        "order_number": order_num,
        "items": [{"productId": "PROD-001", "quantity": -500, "cuttingProcessId": "PROC-ADV"}]
    }
    res = requests.post(f"{BASE_URL}/cutting/order/save", json=payload)
    
    # We expect negative quantities to be rejected as invalid inputs
    assert res.status_code in [400, 422] or res.json().get("code", 0) != 0, "Business logic failure: Allowed order creation with negative quantity!"


# 5. Business Logic Completeness: Empty Order Production Start
def test_adversarial_empty_items_production():
    order_num = f"ORD-ADV-{generate_unique_str()}"
    # Create order with empty items
    res_create = requests.post(f"{BASE_URL}/cutting/order/save", json={
        "order_number": order_num,
        "items": []
    })
    
    # If it was allowed to create, verify if we can start production on it
    if res_create.status_code == 200 and res_create.json().get("code") == 0:
        orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
        order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]
        
        # Try starting production
        res_start = requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
        
        # Starting production on an empty order should be rejected
        assert res_start.status_code in [400, 422] or res_start.json().get("code", 0) != 0, "Business logic failure: Started production on an order with empty items list!"
