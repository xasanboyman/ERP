import requests

BASE_URL = "http://127.0.0.1:8000"

def test_classifier_list_pagination():
    res = requests.get(f"{BASE_URL}/classifier/list", params={"page": 1, "page_size": 10})
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert data["total"] > 400000
    assert len(data["data"]) == 10

def test_classifier_search_brand():
    res = requests.get(f"{BASE_URL}/classifier/list", params={"brand": "Shaffof"})
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert data["total"] > 0
    for item in data["data"]:
        assert "shaffof" in (item["brand_name"] or "").lower()

def test_classifier_by_barcode():
    # 4780014680073 is Shaffof barcode
    res = requests.get(f"{BASE_URL}/classifier/by-barcode/4780014680073")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    item = data["data"]
    assert item["shtrix_code"] == "4780014680073"
    assert item["brand_name"] == "Shaffof"
    assert item["mxik_code"] == "02201001001001002"

def test_classifier_by_mxik():
    # 02201001001001002 is Shaffof MXIK code
    res = requests.get(f"{BASE_URL}/classifier/by-mxik/02201001001001002")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    item = data["data"]
    assert item["mxik_code"] == "02201001001001002"
    assert item["brand_name"] == "Shaffof"

def test_classifier_not_found():
    res = requests.get(f"{BASE_URL}/classifier/by-barcode/0000000000000000000")
    assert res.status_code == 404

    res2 = requests.get(f"{BASE_URL}/classifier/by-mxik/NONEXISTENT_MXIK")
    assert res2.status_code == 404
