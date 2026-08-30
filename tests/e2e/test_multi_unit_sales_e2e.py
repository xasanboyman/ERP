import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from app import models

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_multi_unit_packaging_and_stock_overflow_validation():
    # 1. Create bulk powder product with 2000 kg stock and a 40kg Sack packaging tier
    prod_id = f"PROD-{uuid.uuid4().hex[:8]}"
    pkg_barcode = f"BAR-{uuid.uuid4().hex[:6]}"
    
    prod_payload = {
        "id": prod_id,
        "productName": "Un / Powder Bulk 2000kg",
        "SKU": f"SKU-{uuid.uuid4().hex[:6]}",
        "category": "Oziq-ovqat mahsulotlari",
        "price": 1400.0,
        "cost": 1000.0,
        "quantityInStock": 2000.0,
        "unit": "kg",
        "shtrix_code": f"BASE-{uuid.uuid4().hex[:6]}",
        "packagings": [
            {
                "id": f"PKG-{uuid.uuid4().hex[:6]}",
                "unit_name": "40kg Qop",
                "conversion_factor": 40.0,
                "price": 54000.0,
                "cost": 40000.0,
                "shtrix_code": pkg_barcode,
                "is_base_unit": False
            }
        ]
    }
    
    res = client.post("/product/save", json=prod_payload)
    assert res.status_code == 200
    assert res.json()["code"] == 0

    # 2. Verify Barcode Lookup by Packaging Barcode
    res_bc = client.get(f"/api/product/by-barcode/{pkg_barcode}")
    assert res_bc.status_code == 200
    bc_data = res_bc.json()["data"]
    assert bc_data["id"] == prod_id
    assert bc_data["selected_packaging"] is not None
    assert bc_data["selected_packaging"]["unit_name"] == "40kg Qop"
    assert bc_data["selected_packaging"]["conversion_factor"] == 40.0
    assert bc_data["selected_packaging"]["price"] == 54000.0

    # 3. Stock Overflow Validation: Attempt to buy 100 x 40kg sacks (4,000 kg demand) when stock is only 2,000 kg
    overflow_checkout = {
        "cashier_name": "admin",
        "payment_method": "naqd",
        "items": [
            {
                "product_id": prod_id,
                "product_name": "Un / Powder Bulk 2000kg",
                "price": 54000.0,
                "quantity": 100.0,
                "unit_name": "40kg Qop",
                "conversion_factor": 40.0
            }
        ]
    }
    
    res_overflow = client.post("/sales/checkout", json=overflow_checkout)
    assert res_overflow.status_code == 400
    err_detail = res_overflow.json()["detail"]
    assert "omborda yetarli emas" in err_detail.lower()
    assert "4000.0 kg" in err_detail or "4000 kg" in err_detail

    # 4. Valid Checkout: Buy 40 x 40kg sacks (1,600 kg demand)
    valid_checkout = {
        "cashier_name": "admin",
        "payment_method": "naqd",
        "items": [
            {
                "product_id": prod_id,
                "product_name": "Un / Powder Bulk 2000kg",
                "price": 54000.0,
                "quantity": 40.0,
                "unit_name": "40kg Qop",
                "conversion_factor": 40.0
            }
        ]
    }
    
    res_valid = client.post("/sales/checkout", json=valid_checkout)
    assert res_valid.status_code == 200
    assert res_valid.json()["code"] == 0

    # 5. Verify Remaining Stock is 400 kg (2000 kg - 1600 kg = 400 kg)
    res_detail = client.get(f"/api/product/detail?id={prod_id}")
    assert res_detail.status_code == 200
    stock_after = res_detail.json()["data"]["quantityInStock"]
    assert stock_after == 400.0
