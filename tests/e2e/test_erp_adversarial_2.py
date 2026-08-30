import pytest
import requests
import random

BASE_URL = "http://127.0.0.1:8000"

def generate_unique_str():
    return f"{random.randint(100000, 999999)}"

@pytest.fixture(scope="session", autouse=True)
def setup_stages_and_processes():
    # Ensure standard stage and process are created for reference
    requests.post(f"{BASE_URL}/cutting/stage/save", json={
        "id": "STAGE-STD",
        "name": "Standard Stage",
        "price": 5.0,
        "duration": 60
    })
    requests.post(f"{BASE_URL}/cutting/process/save", json={
        "id": "PROC-STD",
        "name": "Standard Process",
        "stages": [{"id": "STAGE-STD", "name": "Standard Stage"}]
    })

# 1. Start production crash with malformed process stages (AttributeError 500)
def test_start_production_malformed_stages_crash():
    # Create process where stages list contains strings instead of dictionaries
    proc_id = f"PROC-MAL-{generate_unique_str()}"
    res_proc = requests.post(f"{BASE_URL}/cutting/process/save", json={
        "id": proc_id,
        "name": "Malformed Stages Process",
        "stages": ["STAGE-STD"]  # Invalid structure: list of strings
    })
    assert res_proc.status_code == 200
    assert res_proc.json()["code"] == 0

    # Setup product
    sku = f"SKU-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/product/save", json={
        "productName": "Malformed Prod", "SKU": sku, "category": "M", "price": 10.0, "cost": 5.0, "quantityInStock": 5
    })
    products = requests.get(f"{BASE_URL}/product/list", params={"productName": sku}).json()["data"]["list"]
    prod_id = [p["id"] for p in products if p["SKU"] == sku][0]

    # Create Cutting Order referencing this process
    order_num = f"ORD-MAL-{generate_unique_str()}"
    res_order = requests.post(f"{BASE_URL}/cutting/order/save", json={
        "order_number": order_num,
        "items": [{"productId": prod_id, "quantity": 10, "cuttingProcessId": proc_id}]
    })
    assert res_order.json()["code"] == 0
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]

    # Try starting production - this triggers start_production_for_order which loops through stages and calls .get()
    res_start = requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
    
    # We expect the server to reject or handle this gracefully without throwing an HTTP 500 internal server error.
    # If it throws 500, it's an unhandled exception bug.
    assert res_start.status_code != 500, "Severe logic crash: start-production threw HTTP 500 on malformed stages!"
    assert res_start.json().get("code", 0) != 0, "Security/Robustness failure: start-production succeeded with malformed stages!"


# 2. Non-existent responsible users allowed in Cutting Order
def test_nonexistent_responsible_users():
    order_num = f"ORD-USERS-{generate_unique_str()}"
    fake_users = ["nonexistent_user_1", "nonexistent_user_2"]
    
    res = requests.post(f"{BASE_URL}/cutting/order/save", json={
        "order_number": order_num,
        "responsible_user_ids": fake_users,
        "items": [{"productId": "PROD-001", "quantity": 10}]
    })
    
    # We expect the server to validate that responsible users actually exist in the database.
    # If it accepts it, verify that they are returned in the list.
    assert res.status_code in [400, 422] or res.json().get("code", 0) != 0, "Business logic failure: Allowed nonexistent responsible_user_ids!"


# 3. Duplicate responsible users allowed in Cutting Order
def test_duplicate_responsible_users():
    order_num = f"ORD-DUP-{generate_unique_str()}"
    dup_users = ["admin", "admin"]
    
    res = requests.post(f"{BASE_URL}/cutting/order/save", json={
        "order_number": order_num,
        "responsible_user_ids": dup_users,
        "items": [{"productId": "PROD-001", "quantity": 10}]
    })
    assert res.status_code == 200
    assert res.json().get("code") == 0
    
    # Check if duplicate users are returned, or if they were deduplicated.
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    saved_order = [o for o in orders if o["order_number"] == order_num][0]
    
    # We expect the system to deduplicate responsible user ids to avoid UI stack bugs
    assert len(saved_order["responsible_user_ids"]) == 1, "Frontend/Backend parity failure: Allowed duplicate responsible_user_ids!"


# 4. QR Code generation with negative quantity
def test_qr_negative_quantity():
    # Setup order
    order_num = f"ORD-QR-NEG-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/cutting/order/save", json={
        "order_number": order_num,
        "items": [{"productId": "PROD-001", "quantity": 10, "cuttingProcessId": "PROC-STD"}]
    })
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]
    
    # Start production
    requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
    tasks = requests.get(f"{BASE_URL}/cutting/task/list").json()["data"]["list"]
    task_id = [t["id"] for t in tasks if t["orderId"] == order_id][0]
    
    # Try generating QR with negative quantity
    res_qr = requests.post(f"{BASE_URL}/qr/save", json={"taskId": task_id, "quantity": -5})
    
    # Expect failure
    assert res_qr.status_code in [400, 422] or res_qr.json().get("code", 0) != 0, "Business logic failure: Generated QR code with negative quantity!"


# 5. QR Code generation with quantity exceeding task quantity
def test_qr_exceeding_quantity():
    # Setup order
    order_num = f"ORD-QR-EXC-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/cutting/order/save", json={
        "order_number": order_num,
        "items": [{"productId": "PROD-001", "quantity": 10, "cuttingProcessId": "PROC-STD"}]
    })
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]
    
    # Start production
    requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
    tasks = requests.get(f"{BASE_URL}/cutting/task/list").json()["data"]["list"]
    task_id = [t["id"] for t in tasks if t["orderId"] == order_id][0]
    
    # Try generating QR with quantity exceeding task quantity (e.g. 500 when task limit is 10)
    res_qr = requests.post(f"{BASE_URL}/qr/save", json={"taskId": task_id, "quantity": 500})
    
    # Expect failure or rejection to prevent overproduction payouts
    assert res_qr.status_code in [400, 422] or res_qr.json().get("code", 0) != 0, "Business logic failure: Allowed QR code quantity to exceed task quantity!"


# 6. Create salary record for nonexistent worker
def test_salary_nonexistent_worker():
    res_sal = requests.post(f"{BASE_URL}/salary/save", json={
        "workerId": "NONEXISTENT_WORKER_ID",
        "baseSalary": 1000.0,
        "allowance": 100.0,
        "deduction": 50.0,
        "status": "pending"
    })
    
    # We expect creating salary for nonexistent worker to fail
    assert res_sal.status_code in [400, 422] or res_sal.json().get("code", 0) != 0, "Database integrity failure: Created salary for nonexistent worker!"


# 7. Deleting a cutting stage that is referenced by active task
def test_delete_stage_referenced_by_task():
    # Create custom stage
    stage_id = f"STAGE-DEL-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/cutting/stage/save", json={
        "id": stage_id,
        "name": "Temp Stage for Deletion",
        "price": 5.0,
        "duration": 60
    })
    
    proc_id = f"PROC-DEL-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/cutting/process/save", json={
        "id": proc_id,
        "name": "Process with Temp Stage",
        "stages": [{"id": stage_id, "name": "Temp Stage for Deletion"}]
    })

    # Setup order
    order_num = f"ORD-STAGE-DEL-{generate_unique_str()}"
    requests.post(f"{BASE_URL}/cutting/order/save", json={
        "order_number": order_num,
        "items": [{"productId": "PROD-001", "quantity": 10, "cuttingProcessId": proc_id}]
    })
    orders = requests.get(f"{BASE_URL}/cutting/order/list").json()["data"]["list"]
    order_id = [o["id"] for o in orders if o["order_number"] == order_num][0]
    
    # Start production to create tasks
    requests.post(f"{BASE_URL}/cutting/order/start-production", json={"orderId": order_id})
    tasks = requests.get(f"{BASE_URL}/cutting/task/list").json()["data"]["list"]
    task = [t for t in tasks if t["orderId"] == order_id][0]
    
    # Delete the stage
    res_del = requests.post(f"{BASE_URL}/cutting/stage/delete", json={"ids": [stage_id]})
    assert res_del.status_code == 200
    
    # Verify tasks or database state: does the task still reference the deleted stage?
    # Since sqlite constraints are not enabled, the task will still reference it, which is a dangling FK.
    # If task is loaded, does it crash?
    res_tasks = requests.get(f"{BASE_URL}/cutting/task/list")
    assert res_tasks.status_code == 200
    
    # Check if the stage deletion was rejected or if it was allowed to cascade/warn
    # Ideally, deleting a referenced stage should either be rejected or handled cleanly.
    # If the system allows it silently without cascading delete, it violates database integrity.
    # Let's verify that the database has a dangling reference or if it was cleaned.
    tasks_after = res_tasks.json()["data"]["list"]
    matching_task = [t for t in tasks_after if t["id"] == task["id"]][0]
    assert matching_task["stageId"] is None or matching_task["stageId"] == "", "Database integrity failure: stage deletion left dangling task reference!"
