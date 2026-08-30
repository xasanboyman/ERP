import sys
import os
import json
import time
from datetime import datetime, timedelta

# Add Back directory to sys.path
sys.path.insert(0, '/home/xasanboy/ERP/Back')

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app import models, crud, schemas
from app.routers.crm import get_current_user_required

# Setup in-memory SQLite test DB for test harness
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_all_empirical_tests():
    print("=== STARTING EMPIRICAL VERIFICATION & STRESS TESTS ===")
    
    # 1. Setup DB tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create test user
    user = crud.create_user(
        db,
        schemas.UserCreate(
            username="stress_user_m2",
            password="password123",
            full_name="Stress User M2",
            role="admin",
            roleId="1"
        )
    )
    user_id = user.id

    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_get_current_user_required():
        return db.query(models.User).filter(models.User.id == user_id).first()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_required] = override_get_current_user_required

    client = TestClient(app)
    
    # --- TEST SUITE 1: QR PAYLOAD INTEGRITY & EDGE CASES ---
    print("\n--- Running Test Suite 1: QR Payload Integrity & Edge Cases ---")
    device_names_to_test = [
        "Standard POS Terminal",
        "Device with spaces and special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
        "Unicode Device Name: 📱 POS Terminal-Uzbekistan (Kassir 1)",
        "Device\nwith\nnewlines\tand\ttabs"
    ]
    
    for d_name in device_names_to_test:
        response = client.post("/api/device/pair-token", json={"device_name": d_name})
        assert response.status_code == 200, f"Failed for device_name: {d_name}, status: {response.status_code}"
        res_json = response.json()
        assert res_json["code"] == 0
        data = res_json["data"]
        
        # Check required top-level fields
        assert "qr_payload" in data
        assert "token" in data
        assert "device_name" in data
        assert "user_id" in data
        assert "created_at" in data
        
        # Parse qr_payload JSON string
        try:
            qr_obj = json.loads(data["qr_payload"])
        except Exception as e:
            pytest.fail(f"qr_payload is not valid JSON string! Error: {e}, payload: {data['qr_payload']}")
        
        assert isinstance(qr_obj, dict), "qr_payload JSON did not parse to an object"
        
        # Verify required keys in qr_payload
        for req_key in ["token", "user_id", "device_name", "created_at"]:
            assert req_key in qr_obj, f"Key '{req_key}' missing from qr_payload: {qr_obj}"
        
        # Verify data types and values
        assert qr_obj["token"] == data["token"]
        assert qr_obj["user_id"] == user_id
        assert qr_obj["device_name"] == d_name.strip()
        
        # Verify created_at is valid ISO 8601 string
        try:
            parsed_dt = datetime.fromisoformat(qr_obj["created_at"])
            assert isinstance(parsed_dt, datetime)
        except ValueError as ve:
            pytest.fail(f"created_at '{qr_obj['created_at']}' is not a valid ISO datetime format: {ve}")
            
    print("✓ TEST 1 PASSED: QR Payload JSON integrity verified across standard and edge-case device names.")

    # --- TEST SUITE 2: PAIRING TOKEN CREATION RAPID STRESS TEST ---
    print("\n--- Running Test Suite 2: Pairing Token Creation Stress Test ---")
    NUM_REQUESTS = 100
    tokens_generated = []
    pair_codes_generated = []
    
    start_time = time.time()
    for i in range(NUM_REQUESTS):
        resp = client.post("/api/device/pair-token", json={"device_name": f"Stress Device {i}"})
        assert resp.status_code == 200
        res = resp.json()
        token = res["data"]["token"]
        pair_code = res["data"]["pair_code"]
        tokens_generated.append(token)
        pair_codes_generated.append(pair_code)
    duration = time.time() - start_time
    
    print(f"Executed {NUM_REQUESTS} rapid pairing token requests in {duration:.4f} seconds ({NUM_REQUESTS/duration:.2f} req/s).")
    
    # Check uniqueness (zero collision)
    unique_tokens = set(tokens_generated)
    unique_pair_codes = set(pair_codes_generated)
    
    assert len(unique_tokens) == NUM_REQUESTS, f"Token collision detected! Unique: {len(unique_tokens)} vs Total: {NUM_REQUESTS}"
    assert len(unique_pair_codes) == NUM_REQUESTS, f"Pair code collision detected! Unique: {len(unique_pair_codes)} vs Total: {NUM_REQUESTS}"
    
    print("✓ TEST 2 PASSED: 100 rapid token pair requests succeeded with 100% unique tokens and pair codes.")

    # --- TEST SUITE 3: LAST_USED_AT TIMESTAMP THROTTLING MECHANISM ---
    print("\n--- Running Test Suite 3: last_used_at Timestamp Throttling Mechanism ---")
    
    # Create a new token for verification tests
    pair_resp = client.post("/api/device/pair-token", json={"device_name": "Throttling Test Device"})
    dev_token_str = pair_resp.json()["data"]["token"]
    
    # Get initial state from DB
    dev_token_obj = crud.get_device_token_by_token(db, dev_token_str)
    assert dev_token_obj.last_used_at is None, "New token last_used_at should initially be None"
    
    # First verification request
    v_resp1 = client.get("/api/device/verify", headers={"X-Device-Token": dev_token_str})
    assert v_resp1.status_code == 200
    
    db.refresh(dev_token_obj)
    t1 = dev_token_obj.last_used_at
    assert t1 is not None, "First verify request must set last_used_at timestamp"
    print(f"Initial verify call set last_used_at = {t1}")
    
    # 50 consecutive fast requests within < 60 seconds
    print("Executing 50 consecutive verify requests within < 60 seconds...")
    for _ in range(50):
        v_resp = client.get("/api/device/verify", headers={"X-Device-Token": dev_token_str})
        assert v_resp.status_code == 200
        
    db.refresh(dev_token_obj)
    t2 = dev_token_obj.last_used_at
    assert t2 == t1, f"last_used_at was modified during <60s window! {t1} != {t2}"
    print(f"✓ Fast requests within <60s correctly throttled: last_used_at remained {t2}")

    # Now simulate > 60 seconds elapsed by artificially setting last_used_at back 65 seconds
    old_time = datetime.utcnow() - timedelta(seconds=65)
    dev_token_obj.last_used_at = old_time
    db.commit()
    db.refresh(dev_token_obj)
    print(f"Simulating elapsed time > 60s (manually adjusted last_used_at to {old_time})")
    
    # Call verify API again after >60s window
    v_resp_after = client.get("/api/device/verify", headers={"X-Device-Token": dev_token_str})
    assert v_resp_after.status_code == 200
    
    db.refresh(dev_token_obj)
    t3 = dev_token_obj.last_used_at
    assert t3 > old_time, f"last_used_at was NOT updated after >60s! old: {old_time}, new: {t3}"
    print(f"✓ Request after >60s correctly updated last_used_at to {t3}")
    
    print("✓ TEST 3 PASSED: Throttle mechanism verified (<60s retains timestamp, >60s updates timestamp).")

    # --- TEST SUITE 4: ADDITIONAL EDGE CASES & SECURITY CHECKS ---
    print("\n--- Running Test Suite 4: Security & Error Scenarios ---")
    
    # 1. Invalid X-Device-Token header format / non-existent token
    resp_invalid = client.get("/api/device/verify", headers={"X-Device-Token": "non_existent_token_abc123"})
    assert resp_invalid.status_code == 401
    assert "Invalid device token" in resp_invalid.json()["detail"]
    
    # 2. Missing X-Device-Token header
    resp_missing = client.get("/api/device/verify")
    assert resp_missing.status_code == 401
    assert "Missing X-Device-Token" in resp_missing.json()["detail"]
    
    # 3. Revoked token access attempt
    rev_pair = client.post("/api/device/pair-token", json={"device_name": "Device to Revoke"})
    rev_tok_data = rev_pair.json()["data"]
    rev_dev_id = crud.get_device_token_by_token(db, rev_tok_data["token"]).id
    
    # Revoke via DELETE API
    del_resp = client.delete(f"/api/device/revoke/{rev_dev_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["status"] == "revoked"
    
    # Verification attempt with revoked token -> 403 Forbidden
    ver_rev_resp = client.get("/api/device/verify", headers={"X-Device-Token": rev_tok_data["token"]})
    assert ver_rev_resp.status_code == 403
    assert "revoked" in ver_rev_resp.json()["detail"]

    # 4. Revoking already revoked token -> 400 Bad Request
    del_again_resp = client.delete(f"/api/device/revoke/{rev_dev_id}")
    assert del_again_resp.status_code == 400
    assert "already revoked" in del_again_resp.json()["detail"]

    print("✓ TEST 4 PASSED: Security and error scenario verification complete.")

    # Cleanup
    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)
    print("\n=== ALL EMPIRICAL VERIFICATION TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_all_empirical_tests()
