import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
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
def user_a(db_session):
    return crud.create_user(
        db_session,
        schemas.UserCreate(
            username="user_a",
            password="password_a",
            full_name="User Alpha",
            role="admin",
            roleId="1"
        )
    )


@pytest.fixture(scope="function")
def user_b(db_session):
    return crud.create_user(
        db_session,
        schemas.UserCreate(
            username="user_b",
            password="password_b",
            full_name="User Beta",
            role="staff",
            roleId="2"
        )
    )


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ============================================================================
# ADVERSARIAL TEST GROUP 1: Invalid & Corrupted X-Device-Token Headers (401)
# ============================================================================

def test_verify_missing_token_header(client):
    # No header provided -> 401
    resp = client.get("/api/device/verify")
    assert resp.status_code == 401
    assert "Missing X-Device-Token" in resp.json()["detail"]


@pytest.mark.parametrize("corrupted_token", [
    "",
    "   ",
    "invalid_random_string",
    "' OR '1'='1",
    "devtok_" + "x" * 1000,
    "SELECT * FROM device_tokens;",
    "DEVTOK_CASE_SENSITIVE_MISMATCH",
])
def test_verify_corrupted_token_headers(client, corrupted_token):
    # Any corrupted or invalid token -> 401 Unauthorized
    resp = client.get("/api/device/verify", headers={"X-Device-Token": corrupted_token})
    assert resp.status_code == 401
    assert "Invalid device token" in resp.json()["detail"] or "Missing X-Device-Token" in resp.json()["detail"]


# ============================================================================
# ADVERSARIAL TEST GROUP 2: Revoked & Inactive Token Reuse Attempts (403)
# ============================================================================

def test_revoked_token_reuse_multiple_times(client, db_session, user_a):
    app.dependency_overrides[get_current_user_required] = lambda: user_a
    dev_token = crud.create_device_token(db_session, user_id=user_a.id, device_name="Adversarial Terminal")
    token_str = dev_token.token

    # Verify initial valid state -> 200 OK
    resp = client.get("/api/device/verify", headers={"X-Device-Token": token_str})
    assert resp.status_code == 200

    # Revoke token
    crud.revoke_device_token(db_session, device_id=dev_token.id, user_id=user_a.id)

    # Attempt 1 reuse -> 403 Forbidden
    resp1 = client.get("/api/device/verify", headers={"X-Device-Token": token_str})
    assert resp1.status_code == 403
    assert "revoked" in resp1.json()["detail"].lower()

    # Attempt 2 reuse -> 403 Forbidden
    resp2 = client.get("/api/device/verify", headers={"X-Device-Token": token_str})
    assert resp2.status_code == 403
    assert "revoked" in resp2.json()["detail"].lower()

    # Attempt re-revoking already revoked token via API -> 400 Bad Request
    revoke_again = client.delete(f"/api/device/revoke/{dev_token.id}")
    assert revoke_again.status_code == 400
    assert "already revoked" in revoke_again.json()["detail"].lower()


def test_inactive_status_token_denied(client, db_session, user_a):
    dev_token = crud.create_device_token(db_session, user_id=user_a.id, device_name="Inactive POS")
    dev_token.status = "inactive"
    db_session.commit()

    resp = client.get("/api/device/verify", headers={"X-Device-Token": dev_token.token})
    assert resp.status_code == 403
    assert "inactive" in resp.json()["detail"].lower()


# ============================================================================
# ADVERSARIAL TEST GROUP 3: Cross-Account Multi-User Token Access & Revocation
# ============================================================================

def test_cross_account_device_revocation_prevented(client, db_session, user_a, user_b):
    token_a = crud.create_device_token(db_session, user_id=user_a.id, device_name="User A Device")
    token_b = crud.create_device_token(db_session, user_id=user_b.id, device_name="User B Device")

    # User A tries to revoke User B's device -> 403 Forbidden
    app.dependency_overrides[get_current_user_required] = lambda: user_a
    resp_a_revokes_b = client.delete(f"/api/device/revoke/{token_b.id}")
    assert resp_a_revokes_b.status_code == 403
    assert "does not belong to current user" in resp_a_revokes_b.json()["detail"]

    # User B tries to revoke User A's device -> 403 Forbidden
    app.dependency_overrides[get_current_user_required] = lambda: user_b
    resp_b_revokes_a = client.delete(f"/api/device/revoke/{token_a.id}")
    assert resp_b_revokes_a.status_code == 403
    assert "does not belong to current user" in resp_b_revokes_a.json()["detail"]

    # Verify device status remains active for both devices
    db_session.refresh(token_a)
    db_session.refresh(token_b)
    assert token_a.status == "active"
    assert token_b.status == "active"


def test_cross_account_device_list_isolation(client, db_session, user_a, user_b):
    crud.create_device_token(db_session, user_id=user_a.id, device_name="A Device 1")
    crud.create_device_token(db_session, user_id=user_a.id, device_name="A Device 2")
    crud.create_device_token(db_session, user_id=user_b.id, device_name="B Device 1")

    # Query as User A
    app.dependency_overrides[get_current_user_required] = lambda: user_a
    res_a = client.get("/api/device/list").json()

    # Query as User B
    app.dependency_overrides[get_current_user_required] = lambda: user_b
    res_b = client.get("/api/device/list").json()

    assert res_a["data"]["total"] == 2
    assert all(item["device_name"].startswith("A Device") for item in res_a["data"]["list"])

    assert res_b["data"]["total"] == 1
    assert res_b["data"]["list"][0]["device_name"] == "B Device 1"


# ============================================================================
# ADVERSARIAL TEST GROUP 4: Missing Database Records & Deleted User Edge Cases
# ============================================================================

def test_verify_token_with_deleted_user(client, db_session):
    # Disable foreign key checks temporarily to insert token with missing user
    db_session.execute(text("PRAGMA foreign_keys=OFF;"))
    ghost_token = models.DeviceToken(
        user_id=99999,
        device_name="Ghost Device",
        token="devtok_ghost_user_token_123456",
        status="active"
    )
    db_session.add(ghost_token)
    db_session.commit()
    db_session.execute(text("PRAGMA foreign_keys=ON;"))

    # Attempting to verify token for missing user record -> 401 Unauthorized
    resp = client.get("/api/device/verify", headers={"X-Device-Token": ghost_token.token})
    assert resp.status_code == 401
    assert "User associated with device token not found" in resp.json()["detail"]


def test_revoke_non_existent_device_id(client, user_a):
    app.dependency_overrides[get_current_user_required] = lambda: user_a
    # Attempting to revoke device ID 999999 -> 404 Not Found
    resp = client.delete("/api/device/revoke/999999")
    assert resp.status_code == 404
    assert "Device token not found" in resp.json()["detail"]


def test_pair_token_non_existent_target_user(client, user_a):
    app.dependency_overrides[get_current_user_required] = lambda: user_a
    # Attempting to pair token for non-existent target user ID -> 404 Not Found
    resp = client.post("/api/device/pair-token", json={"device_name": "Test", "user_id": 888888})
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_pair_token_empty_device_name(client, user_a):
    app.dependency_overrides[get_current_user_required] = lambda: user_a
    # Empty device name -> 400 Bad Request
    resp = client.post("/api/device/pair-token", json={"device_name": "   "})
    assert resp.status_code == 400
    assert "Device name is required" in resp.json()["detail"]
