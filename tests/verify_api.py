import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def verify_parity():
    print("--- Starting Backend API Parity Verification ---")
    
    # 1. Fetch current order list
    print("\n1. Fetching current cutting orders list...")
    res = requests.get(f"{BASE_URL}/cutting/order/list")
    if res.status_code != 200:
        print(f"FAILED to fetch orders. Status: {res.status_code}")
        sys.exit(1)
    
    data = res.json()
    print(f"Success. Current order count: {data['data']['total']}")
    
    # 2. Create a new cutting order with responsible_user_ids
    print("\n2. Creating a new cutting order with responsible_user_ids: ['user_abc', 'user_xyz']...")
    order_number = "ORD-VERIFY-999"
    payload = {
        "order_number": order_number,
        "project": "Verification Project",
        "order_name": "API Parity Test",
        "responsible_user_ids": ["user_abc", "user_xyz"],
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 100,
                "category": "Verification"
            }
        ]
    }
    
    res_save = requests.post(f"{BASE_URL}/cutting/order/save", json=payload)
    if res_save.status_code != 200 or res_save.json().get("code") != 0:
        print(f"FAILED to save order. Response: {res_save.text}")
        sys.exit(1)
    print("Success. Order created successfully.")
    
    # 3. Retrieve the order and verify responsible_user_ids
    print("\n3. Retrieving the order and verifying deserialization of responsible_user_ids...")
    res_list = requests.get(f"{BASE_URL}/cutting/order/list")
    orders = res_list.json()["data"]["list"]
    
    found_order = [o for o in orders if o["order_number"] == order_number]
    if not found_order:
        print("FAILED: Saved order not found in list.")
        sys.exit(1)
    
    order = found_order[0]
    print(f"Retrieved Order ID: {order['id']}")
    print(f"responsible_user_ids: {order['responsible_user_ids']} (Type: {type(order['responsible_user_ids']).__name__})")
    
    assert order["responsible_user_ids"] == ["user_abc", "user_xyz"], "Mismatch in responsible_user_ids after creation"
    print("Verification passed: responsible_user_ids correctly saved and deserialized.")
    
    # 4. Update the order with new responsible_user_ids
    print("\n4. Updating the order with responsible_user_ids: ['user_updated']...")
    update_payload = {
        "id": order["id"],
        "order_number": order_number,
        "project": "Verification Project",
        "order_name": "API Parity Test (Updated)",
        "responsible_user_ids": ["user_updated"],
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 100,
                "category": "Verification"
            }
        ]
    }
    
    res_update = requests.post(f"{BASE_URL}/cutting/order/save", json=update_payload)
    if res_update.status_code != 200 or res_update.json().get("code") != 0:
        print(f"FAILED to update order. Response: {res_update.text}")
        sys.exit(1)
    print("Success. Order updated successfully.")
    
    # 5. Retrieve again and verify the update
    print("\n5. Retrieving the updated order and verifying responsible_user_ids...")
    res_list2 = requests.get(f"{BASE_URL}/cutting/order/list")
    orders2 = res_list2.json()["data"]["list"]
    
    found_order2 = [o for o in orders2 if o["id"] == order["id"]]
    if not found_order2:
        print("FAILED: Updated order not found in list.")
        sys.exit(1)
        
    order2 = found_order2[0]
    print(f"responsible_user_ids: {order2['responsible_user_ids']} (Type: {type(order2['responsible_user_ids']).__name__})")
    
    assert order2["responsible_user_ids"] == ["user_updated"], "Mismatch in responsible_user_ids after update"
    print("Verification passed: responsible_user_ids correctly updated and deserialized.")
    
    # 6. Delete the order
    print("\n6. Cleaning up: Deleting the test cutting order...")
    res_del = requests.post(f"{BASE_URL}/cutting/order/delete", json={"ids": [order["id"]]})
    if res_del.status_code != 200 or res_del.json().get("code") != 0:
        print(f"FAILED to delete order. Response: {res_del.text}")
        sys.exit(1)
    print("Success. Test order deleted and cleaned up.")
    
    print("\n--- All Parity Verifications Passed Successfully ---")

if __name__ == "__main__":
    verify_parity()
