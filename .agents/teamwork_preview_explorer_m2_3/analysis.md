# Exploration & Design Analysis Report: Backend Device Token Management & Verification API (Milestone 2 - R1)

**Agent**: Explorer 3  
**Working Directory**: `/home/xasanboy/ERP/.agents/teamwork_preview_explorer_m2_3`  
**Scope Reference**: `/home/xasanboy/ERP/.agents/sub_orch_m2/SCOPE.md`  
**Date**: 2026-08-09  

---

## 1. Executive Summary

This report presents a thorough investigation of the backend architecture of the ERP system (`/home/xasanboy/ERP/Back`) and provides the design specifications for **Milestone 2: Backend Device Token Management & Verification API (R1)**.

Specifically, this report covers:
1. Analysis of existing CRUD patterns in `Back/app/crud.py` and router registration in `Back/app/main.py`.
2. Detailed design of CRUD functions for `DeviceToken`.
3. Detailed design of router endpoints:
   - `POST /api/device/pair-token`
   - `GET /api/device/list`
   - `DELETE /api/device/revoke/{device_id}`
4. Analysis of Pytest testing environment (`Back/venv/bin/pytest`), runner configuration, test structure, and proposed test suite (`test_device.py`).

---

## 2. Architecture & Code Structure Analysis

### 2.1 File & Directory Layout
- **`Back/app/models.py`**: Defines SQLAlchemy ORM models (`User`, `Role`, `Product`, `Worker`, `ActivityLog`, etc.).
- **`Back/app/schemas.py`**: Defines Pydantic data validation & serialization schemas.
- **`Back/app/crud.py`**: Contains database access and manipulation helper functions accepting `db: Session`.
- **`Back/app/routers/`**: Contains modular FastAPI routers (`auth.py`, `crm.py`, `worker.py`, `qr.py`, `sales.py`, etc.).
- **`Back/app/main.py`**: Initializes the FastAPI application, mounts static files, adds middleware (CORS, token expiration handler, integrity error handler), and includes all routers using `app.include_router()`.

### 2.2 CRUD Conventions in `crud.py`
Examining `crud.py` reveals the following key conventions:
- **Session Management**: All CRUD functions accept `db: Session` as their first argument.
- **ORM Queries**: Use `db.query(models.ModelName)`. Filters are applied using `.filter(models.Model.field == val)`.
- **Object Creation**:
  ```python
  db_obj = models.ModelName(**data)
  db.add(db_obj)
  db.commit()
  db.refresh(db_obj)
  return db_obj
  ```
- **Object Updates**: Query existing record, update fields directly, then `db.commit()` and `db.refresh(db_obj)`.
- **Deletion/Revocation**: Deletion removes record via `db.delete(db_obj)`; status updating sets `db_obj.status = "revoked"`.

### 2.3 Router Registration & Endpoint Patterns in `main.py`
In `main.py`, routers are imported and registered as follows:
```python
from .routers import auth, role, department, branch, product, worker, salary, analytics, activity, cutting, qr, staff_hr, ai, classifier, sales, device

app.include_router(device.router, tags=["Device Management"])
```
Existing routers use `APIRouter()` or `APIRouter(prefix="/api/device", tags=["Device Management"])`.
Standard response format across routers:
```json
{
  "code": 0,
  "data": { ... }
}
```
For error cases, HTTP standard status codes (401, 403, 404, 400) or error response envelopes `{"code": 404, "message": "..."}` are returned.

---

## 3. Detailed Endpoint & CRUD Design for Device Tokens

### 3.1 Data Model (`models.DeviceToken`)
*(Assumed model structure created by Explorer 1)*
```python
class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_name = Column(String, default="Mobile Terminal", nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="active", index=True) # "active" | "revoked"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="device_tokens")
```

### 3.2 Pydantic Schemas (`schemas.py`)
```python
class DevicePairRequest(BaseModel):
    device_name: Optional[str] = "Mobile Terminal"

class DevicePairResponse(BaseModel):
    id: int
    user_id: int
    device_name: str
    token: str
    qr_payload: str
    status: str
    created_at: str

class DeviceOut(BaseModel):
    id: int
    user_id: int
    device_name: str
    token: str
    status: str
    created_at: Optional[str] = None
    last_used_at: Optional[str] = None

class DeviceRevokeResponse(BaseModel):
    id: int
    status: str
    message: str
```

### 3.3 CRUD Functions Design (`crud.py`)

#### 1. `create_device_token`
```python
import secrets
import json

def create_device_token(db: Session, user_id: int, device_name: str = "Mobile Terminal") -> models.DeviceToken:
    raw_token = f"devtok_{secrets.token_urlsafe(32)}"
    device_token = models.DeviceToken(
        user_id=user_id,
        device_name=device_name or "Mobile Terminal",
        token=raw_token,
        status="active",
        created_at=datetime.datetime.utcnow()
    )
    db.add(device_token)
    db.commit()
    db.refresh(device_token)
    return device_token
```

#### 2. `get_user_device_tokens`
```python
def get_user_device_tokens(db: Session, user_id: int, status: Optional[str] = None) -> list[models.DeviceToken]:
    query = db.query(models.DeviceToken).filter(models.DeviceToken.user_id == user_id)
    if status:
        query = query.filter(models.DeviceToken.status == status)
    return query.order_by(models.DeviceToken.created_at.desc()).all()
```

#### 3. `get_device_token_by_id`
```python
def get_device_token_by_id(db: Session, device_id: int, user_id: Optional[int] = None) -> Optional[models.DeviceToken]:
    query = db.query(models.DeviceToken).filter(models.DeviceToken.id == device_id)
    if user_id is not None:
        query = query.filter(models.DeviceToken.user_id == user_id)
    return query.first()
```

#### 4. `get_device_token_by_token`
```python
def get_device_token_by_token(db: Session, token_str: str) -> Optional[models.DeviceToken]:
    return db.query(models.DeviceToken).filter(models.DeviceToken.token == token_str).first()
```

#### 5. `revoke_device_token`
```python
def revoke_device_token(db: Session, device_id: int, user_id: Optional[int] = None) -> Optional[models.DeviceToken]:
    dev_token = get_device_token_by_id(db, device_id, user_id=user_id)
    if not dev_token:
        return None
    dev_token.status = "revoked"
    db.commit()
    db.refresh(dev_token)
    return dev_token
```

#### 6. `touch_device_token_last_used`
```python
def touch_device_token_last_used(db: Session, device_token: models.DeviceToken):
    device_token.last_used_at = datetime.datetime.utcnow()
    db.commit()
```

---

### 3.4 Router Logic Design (`Back/app/routers/device.py`)

```python
import json
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models, schemas
from app.routers.crm import get_current_user_required
from app.routers.activity import log_activity

router = APIRouter(prefix="/api/device", tags=["Device Management"])

@router.post("/pair-token")
def pair_device_token(
    body: schemas.DevicePairRequest = Body(default_factory=schemas.DevicePairRequest),
    current_user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    Generate a new secure device pairing token and QR code payload string for logged-in user.
    """
    device_name = body.device_name if body and body.device_name else "Mobile Terminal"
    device_token = crud.create_device_token(db, user_id=current_user.id, device_name=device_name)
    
    # Construct QR Code payload (JSON formatted string with token, user_id, device_name, timestamp)
    qr_payload_dict = {
        "token": device_token.token,
        "user_id": current_user.id,
        "device_name": device_token.device_name,
        "created_at": device_token.created_at.isoformat() if device_token.created_at else ""
    }
    qr_payload_str = json.dumps(qr_payload_dict)

    log_activity(
        db,
        actor=current_user.username,
        action="paired_device",
        entity="device_token",
        entity_id=str(device_token.id),
        entity_name=f"Device {device_token.device_name}"
    )

    return {
        "code": 0,
        "data": {
            "id": device_token.id,
            "user_id": device_token.user_id,
            "device_name": device_token.device_name,
            "token": device_token.token,
            "qr_payload": qr_payload_str,
            "status": device_token.status,
            "created_at": str(device_token.created_at)
        }
    }


@router.get("/list")
def list_user_devices(
    current_user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    List active & connected devices for the authenticated user.
    """
    tokens = crud.get_user_device_tokens(db, user_id=current_user.id)
    devices_data = []
    for t in tokens:
        devices_data.append({
            "id": t.id,
            "user_id": t.user_id,
            "device_name": t.device_name,
            "token": t.token,
            "status": t.status,
            "created_at": str(t.created_at) if t.created_at else None,
            "last_used_at": str(t.last_used_at) if t.last_used_at else None
        })

    return {
        "code": 0,
        "data": {
            "total": len(devices_data),
            "list": devices_data
        }
    }


@router.delete("/revoke/{device_id}")
def revoke_device(
    device_id: int,
    current_user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    Revoke a device token (sets status="revoked").
    """
    # Allow revocation if superadmin or if token belongs to current user
    is_admin = current_user.role in ["Super Administrator", "admin"] or current_user.roleId == "1"
    target_user_id = None if is_admin else current_user.id

    dev_token = crud.revoke_device_token(db, device_id=device_id, user_id=target_user_id)
    if not dev_token:
        raise HTTPException(
            status_code=404,
            detail="Device token not found or access denied."
        )

    log_activity(
        db,
        actor=current_user.username,
        action="revoked_device",
        entity="device_token",
        entity_id=str(dev_token.id),
        entity_name=f"Device {dev_token.device_name}"
    )

    return {
        "code": 0,
        "message": "Device token revoked successfully",
        "data": {
            "id": dev_token.id,
            "status": dev_token.status
        }
    }
```

---

## 4. Pytest Environment & Testing Strategy

### 4.1 Pytest Execution Infrastructure
- **Python Virtualenv**: `/home/xasanboy/ERP/Back/venv`
- **Pytest Binary**: `/home/xasanboy/ERP/Back/venv/bin/pytest`
- **Invocation Command**:
  ```bash
  cd /home/xasanboy/ERP
  ./Back/venv/bin/pytest Back/tests/test_device.py -v
  ```
  or
  ```bash
  cd /home/xasanboy/ERP/Back
  ./venv/bin/python -m pytest tests/test_device.py -v
  ```

### 4.2 Unit/Integration Test Suite Design (`Back/tests/test_device.py`)
Using FastAPI `TestClient` and SQLite test session override:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_device.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_pair_token_endpoint():
    # Login or obtain token
    login_res = client.post("/user/login", json={"username": "admin", "password": "admin"})
    auth_token = login_res.json()["data"]["token"]

    response = client.post(
        "/api/device/pair-token",
        headers={"Authorization": auth_token},
        json={"device_name": "Scanner Terminal 1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["device_name"] == "Scanner Terminal 1"
    assert "token" in data["data"]
    assert "qr_payload" in data["data"]

def test_list_devices_endpoint():
    login_res = client.post("/user/login", json={"username": "admin", "password": "admin"})
    auth_token = login_res.json()["data"]["token"]

    response = client.get(
        "/api/device/list",
        headers={"Authorization": auth_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["total"] >= 1

def test_revoke_device_endpoint():
    login_res = client.post("/user/login", json={"username": "admin", "password": "admin"})
    auth_token = login_res.json()["data"]["token"]

    # First pair a new device
    pair_res = client.post(
        "/api/device/pair-token",
        headers={"Authorization": auth_token},
        json={"device_name": "Temp Device"}
    )
    device_id = pair_res.json()["data"]["id"]

    # Revoke it
    revoke_res = client.delete(
        f"/api/device/revoke/{device_id}",
        headers={"Authorization": auth_token}
    )
    assert revoke_res.status_code == 200
    assert revoke_res.json()["data"]["status"] == "revoked"
```

---

## 5. Synthesis & Implementer Guidance

1. **`Back/app/crud.py`**: Add `create_device_token`, `get_user_device_tokens`, `get_device_token_by_id`, `get_device_token_by_token`, `revoke_device_token`, `touch_device_token_last_used`.
2. **`Back/app/schemas.py`**: Add `DevicePairRequest`, `DevicePairResponse`, `DeviceOut`, `DeviceRevokeResponse`.
3. **`Back/app/routers/device.py`**: Implement router with `@router.post("/pair-token")`, `@router.get("/list")`, `@router.delete("/revoke/{device_id}")`.
4. **`Back/app/main.py`**: Add `from .routers import device` and `app.include_router(device.router, tags=["Device Management"])`.
5. **`Back/tests/test_device.py`**: Implement pytest unit test suite and run with `./Back/venv/bin/pytest`.
