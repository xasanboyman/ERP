import pytest
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app import models, crud, schemas
from app.routers.crm import get_current_user_required
from sqlalchemy.pool import StaticPool

# Setup in-memory SQLite test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(db_session):
    user = crud.create_user(
        db_session,
        schemas.UserCreate(
            username="device_user",
            password="password123",
            full_name="Device Test User",
            role="admin",
            roleId="1"
        )
    )
    return user


@pytest.fixture(scope="function")
def client(db_session, test_user):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user_required():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_required] = override_get_current_user_required
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# Unit Tests for CRUD
def test_crud_device_token_lifecycle(db_session, test_user):
    # Create token
    dev_token = crud.create_device_token(db_session, user_id=test_user.id, device_name="POS Terminal 1")
    assert dev_token.id is not None
    assert dev_token.user_id == test_user.id
    assert dev_token.device_name == "POS Terminal 1"
    assert dev_token.token.startswith("devtok_")
    assert dev_token.status == "active"
    assert dev_token.created_at is not None
    assert dev_token.last_used_at is None

    # Get by token
    fetched = crud.get_device_token_by_token(db_session, token=dev_token.token)
    assert fetched is not None
    assert fetched.id == dev_token.id

    # Get by id
    fetched_by_id = crud.get_device_token_by_id(db_session, device_id=dev_token.id, user_id=test_user.id)
    assert fetched_by_id is not None
    assert fetched_by_id.token == dev_token.token

    # Get user device tokens
    tokens = crud.get_user_device_tokens(db_session, user_id=test_user.id)
    assert len(tokens) == 1
    assert tokens[0].id == dev_token.id

    # Update last_used_at
    crud.update_device_token_last_used(db_session, dev_token)
    assert dev_token.last_used_at is not None

    # Revoke
    revoked = crud.revoke_device_token(db_session, device_id=dev_token.id, user_id=test_user.id)
    assert revoked.status == "revoked"

    # Get active tokens only
    active_tokens = crud.get_user_device_tokens(db_session, user_id=test_user.id, status="active")
    assert len(active_tokens) == 0


# Integration Tests for API Endpoints
def test_pair_device_token_api(client, test_user):
    response = client.post("/api/device/pair-token", json={"device_name": "Warehouse Tablet"})
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["code"] == 0
    data = res_json["data"]
    assert data["device_name"] == "Warehouse Tablet"
    assert data["token"].startswith("devtok_")
    assert "qr_payload" in data
    qr_data = json.loads(data["qr_payload"])
    assert qr_data["token"] == data["token"]
    assert qr_data["device_name"] == "Warehouse Tablet"


def test_list_device_tokens_api(client, test_user, db_session):
    crud.create_device_token(db_session, user_id=test_user.id, device_name="Device A")
    crud.create_device_token(db_session, user_id=test_user.id, device_name="Device B")

    response = client.get("/api/device/list")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["code"] == 0
    data = res_json["data"]
    assert data["total"] == 2
    assert len(data["list"]) == 2


def test_verify_device_token_success_and_failures(client, db_session, test_user):
    # 1. Missing header -> 401
    resp = client.get("/api/device/verify")
    assert resp.status_code == 401
    assert "Missing X-Device-Token" in resp.json()["detail"]

    # 2. Invalid token -> 401
    resp = client.get("/api/device/verify", headers={"X-Device-Token": "invalid_token_123"})
    assert resp.status_code == 401
    assert "Invalid device token" in resp.json()["detail"]

    # 3. Active token -> 200 OK
    dev_token = crud.create_device_token(db_session, user_id=test_user.id, device_name="Counter Scanner")
    resp = client.get("/api/device/verify", headers={"X-Device-Token": dev_token.token})
    assert resp.status_code == 200
    res_json = resp.json()
    assert res_json["code"] == 0
    assert res_json["data"]["device_name"] == "Counter Scanner"
    assert res_json["data"]["device_id"] == dev_token.id

    # Verify last_used_at updated
    db_session.refresh(dev_token)
    assert dev_token.last_used_at is not None

    # 4. Revoked token -> 403 Forbidden
    crud.revoke_device_token(db_session, device_id=dev_token.id)
    resp = client.get("/api/device/verify", headers={"X-Device-Token": dev_token.token})
    assert resp.status_code == 403
    assert "revoked" in resp.json()["detail"]


def test_revoke_device_token_api_flow(client, db_session, test_user):
    dev_token = crud.create_device_token(db_session, user_id=test_user.id, device_name="Mobile POS")
    token_str = dev_token.token
    device_id = dev_token.id

    # Access verify should succeed first
    resp_before = client.get("/api/device/verify", headers={"X-Device-Token": token_str})
    assert resp_before.status_code == 200

    # Call DELETE /api/device/revoke/{device_id}
    revoke_resp = client.delete(f"/api/device/revoke/{device_id}")
    assert revoke_resp.status_code == 200
    assert revoke_resp.json()["code"] == 0
    assert revoke_resp.json()["data"]["status"] == "revoked"

    # Subsequent request using X-Device-Token must return 403 Forbidden
    resp_after = client.get("/api/device/verify", headers={"X-Device-Token": token_str})
    assert resp_after.status_code == 403
    assert "revoked" in resp_after.json()["detail"]


def test_revoke_nonexistent_or_other_user_device(client, db_session, test_user):
    # 1. Non-existent device_id
    resp = client.delete("/api/device/revoke/99999")
    assert resp.status_code == 404

    # 2. Device belonging to another user
    other_user = crud.create_user(
        db_session,
        schemas.UserCreate(username="other_user", password="password")
    )
    other_token = crud.create_device_token(db_session, user_id=other_user.id, device_name="Other Device")

    resp = client.delete(f"/api/device/revoke/{other_token.id}")
    assert resp.status_code == 403
