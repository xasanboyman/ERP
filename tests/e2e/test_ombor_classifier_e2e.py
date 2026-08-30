import pytest
import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

def test_ombor_classifier_flow():
    # 1. Direct Barcode lookup for 'Shaffof' (Shtrix code: 4780014680073)
    barcode = "4780014680073"
    resp = requests.get(f"{BASE_URL}/classifier/by-barcode/{barcode}")
    assert resp.status_code == 200
    res_json = resp.json()
    assert res_json["code"] == 0
    item = res_json["data"]
    assert item is not None
    assert item["shtrix_code"] == barcode
    assert "Shaffof" in (item["brand_name"] or "") or "Shaffof" in (item["mxik_name"] or "")

    # 2. Add product to Ombor using classifier data
    unique_sku = f"SKU-TEST-{uuid.uuid4().hex[:8]}"
    payload = {
        "productName": item["mxik_name"],
        "SKU": unique_sku,
        "category": "Ichimliklar va suvlar",
        "price": 4500.0,
        "cost": 2800.0,
        "quantityInStock": 150,
        "status": 1,
        "classifier_id": item["id"],
        "shtrix_code": item["shtrix_code"],
        "mxik_code": item["mxik_code"],
        "brand_name": item["brand_name"],
        "attribute_name": item["attribute_name"],
        "unit": item["unit"] or "dona",
        "remark": "E2E Ombor test kirim"
    }

    save_resp = requests.post(f"{BASE_URL}/product/save", json=payload)
    assert save_resp.status_code == 200
    assert save_resp.json()["code"] == 0

    # 3. Retrieve product list and filter by barcode
    list_resp = requests.get(f"{BASE_URL}/product/list", params={"shtrix_code": barcode})
    assert list_resp.status_code == 200
    list_data = list_resp.json()["data"]["list"]
    assert len(list_data) >= 1
    found = [p for p in list_data if p["SKU"] == unique_sku][0]
    assert found["brand_name"] == item["brand_name"]
    assert found["mxik_code"] == item["mxik_code"]
    assert found["shtrix_code"] == barcode
    assert found["quantityInStock"] == 150
    assert found["cost"] == 2800.0
    assert found["price"] == 4500.0

    # Cleanup created product
    del_resp = requests.post(f"{BASE_URL}/product/delete", json={"ids": [found["id"]]})
    assert del_resp.status_code == 200
    assert del_resp.json()["code"] == 0
