# Exploration Analysis Report: Milestone 2 — Backend Device Token Management & Verification API (R1)

**Working Directory**: `/home/xasanboy/ERP/.agents/teamwork_preview_explorer_m2_1`  
**Target Workspace**: `/home/xasanboy/ERP`  
**Date**: 2026-08-09  
**Status**: Read-only Exploration Completed  

---

## 1. Executive Summary & Objective

The objective of Milestone 2 (Requirement R1) is to establish a robust backend device token management and verification mechanism within the ERP system. This includes:
1. Defining the `DeviceToken` SQLAlchemy ORM model linked to the existing `User` model.
2. Defining corresponding Pydantic schemas in `Back/app/schemas.py` for device pairing requests/responses and device token listing.
3. Outlining CRUD helper functions in `Back/app/crud.py` for issuing, retrieving, revoking, and updating device tokens.
4. Designing FastAPI dependency (`get_current_device_token`) parsing the `X-Device-Token` header for security verification.
5. Providing API endpoints in `/api/device/*` for device pairing (`/pair-token`), listing (`/list`), and revocation (`/revoke/{device_id}`).

This report details the exact structure of existing files, code conventions, database relationships, and exact specification for implementation.

---

## 2. Existing Codebase Analysis

### 2.1 Database & Engine Configuration (`Back/app/database.py`)
- **Base Class**: `Base = declarative_base()` (Line 20).
- **Engine**: SQLite database loaded from `settings.DATABASE_URL` with `connect_args={"check_same_thread": False}` (Line 15-17).
- **Foreign Key Enforcement**: SQLite PRAGMA `foreign_keys=ON` is enabled on connect (Line 10-13).
- **Session Dependency**: `get_db()` yields `SessionLocal()` (Line 22-27).

### 2.2 Table Initialization & Seed Scripts (`Back/app/main.py`, `Back/seed.py`)
- In `Back/app/main.py` (Line 12): `Base.metadata.create_all(bind=engine)` is called on backend application import/startup.
- In `Back/seed.py` (Line 10): `Base.metadata.create_all(bind=engine)` is called during seed script execution.
- **Key Takeaway**: Adding the `DeviceToken` class to `Back/app/models.py` (which imports `Base` from `.database`) will automatically trigger SQLite table creation upon application startup or seed execution without requiring manual Alembic migrations.

### 2.3 Existing `User` Model (`Back/app/models.py`)
Lines 17–30 in `Back/app/models.py`:
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)  # Integer primary key
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    role = Column(String, default="worker")
    roleId = Column(String, default="2")
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    department_id = Column(String, nullable=True)
    avatar = Column(Text, nullable=True)
    create_time = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    permissions = Column(JSON, default=list)
```
- **Key Observation**: `User.id` is typed as `Integer` (autoincrement primary key).
- **Implication for `DeviceToken`**: The foreign key `user_id` in `DeviceToken` MUST be `Integer`, referencing `users.id`.

### 2.4 Pydantic Schemas Style (`Back/app/schemas.py`)
- Pydantic Version: `pydantic>=2.0.0` (as per `Back/requirements.txt`).
- Response models use `class Config: from_attributes = True` for ORM compatibility.
- Standard pattern uses wrapper responses with `"code": 0` and `"data": ...`.

---

## 3. Detailed Specification & Proposed Design

### 3.1 SQLAlchemy `DeviceToken` Model (`Back/app/models.py`)

Proposed ORM Class Definition:
```python
class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_name = Column(String, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="active", nullable=False, index=True)  # "active", "revoked"
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="device_tokens")
```

#### Field Specifications:
| Field Name | Type | Key / Constraint | Description |
|---|---|---|---|
| `id` | `Integer` | Primary Key, `autoincrement=True` | Unique integer identifier for device token entry |
| `user_id` | `Integer` | Foreign Key -> `users.id` (`ondelete="CASCADE"`) | ID of the user who paired/owns the device |
| `device_name` | `String` | Non-nullable | Descriptive device name (e.g. "Scanner Terminal #1", "Warehouse PDA") |
| `token` | `String` | Unique, Indexed, Non-nullable | Secure random token (e.g. 64-char hex string) |
| `status` | `String` | Default: `"active"`, Indexed | Token status: `"active"` or `"revoked"` |
| `created_at` | `DateTime` | Default: `utcnow` | Timestamp when device pairing token was created |
| `last_used_at` | `DateTime` | Nullable | Timestamp of last successful authorization with this token |

---

### 3.2 Pydantic Schemas (`Back/app/schemas.py`)

Proposed Schema Definitions:
```python
# Device Token Schemas
class DevicePairTokenCreate(BaseModel):
    device_name: Optional[str] = "Scanner Terminal"

class DevicePairTokenResponse(BaseModel):
    id: int
    user_id: int
    device_name: str
    token: str
    qr_payload: str
    status: str
    created_at: datetime.datetime
    last_used_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class DeviceTokenResponse(BaseModel):
    id: int
    user_id: int
    device_name: str
    token: str
    status: str
    created_at: datetime.datetime
    last_used_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class DeviceTokenListResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: List[DeviceTokenResponse]
```

#### Payload QR Code Format:
The `qr_payload` string generated during pairing (`/pair-token`) should contain a JSON-stringified object:
```json
{
  "token": "<sec_token_hex>",
  "device_name": "<device_name>",
  "user_id": 1,
  "created_at": "<iso_timestamp>"
}
```

---

### 3.3 CRUD Functions (`Back/app/crud.py`)

Required helper functions to append to `Back/app/crud.py`:

1. `create_device_token(db: Session, user_id: int, device_name: str) -> models.DeviceToken`
   - Generates a cryptographically secure token using `secrets.token_hex(32)`.
   - Creates and commits `models.DeviceToken(user_id=user_id, device_name=device_name, token=token, status="active")`.
   - Returns the created ORM instance.

2. `get_device_tokens_by_user(db: Session, user_id: int, status_filter: Optional[str] = None) -> List[models.DeviceToken]`
   - Queries `models.DeviceToken` filtering by `user_id == user_id`.
   - If `status_filter` is provided (e.g. `"active"`), filters by `status == status_filter`.
   - Orders by `created_at.desc()`.

3. `get_device_token_by_token(db: Session, token: str) -> Optional[models.DeviceToken]`
   - Queries `models.DeviceToken` by `models.DeviceToken.token == token`.

4. `revoke_device_token(db: Session, device_id: int, user_id: int) -> Optional[models.DeviceToken]`
   - Finds device token by `id == device_id` and `user_id == user_id`.
   - If found, sets `status = "revoked"` and commits.
   - Returns updated token record or `None`.

5. `update_device_token_last_used(db: Session, token_obj: models.DeviceToken) -> models.DeviceToken`
   - Updates `token_obj.last_used_at = datetime.datetime.utcnow()`.
   - Commits changes and returns `token_obj`.

---

### 3.4 Router & Security Dependency (`Back/app/routers/device.py`)

#### FastAPI Auth Dependency:
```python
def get_current_device_token(
    x_device_token: Optional[str] = Header(None, alias="X-Device-Token"),
    db: Session = Depends(get_db)
) -> models.DeviceToken:
    if not x_device_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Device-Token header is missing"
        )
    
    device_token = crud.get_device_token_by_token(db, x_device_token)
    if not device_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device token"
        )
    
    if device_token.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device token has been revoked"
        )
    
    if not device_token.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Associated user account not found"
        )
    
    # Update last_used_at timestamp on successful verification
    crud.update_device_token_last_used(db, device_token)
    return device_token
```

#### API Endpoints Specification:

1. **`POST /api/device/pair-token`**
   - **Auth**: Requires standard user authentication (`Authorization: Bearer <jwt>`).
   - **Request Body**: `schemas.DevicePairTokenCreate` (e.g. `{"device_name": "Warehouse Scanner 1"}`).
   - **Response**: `{"code": 0, "data": schemas.DevicePairTokenResponse}`.

2. **`GET /api/device/list`**
   - **Auth**: Requires standard user authentication.
   - **Query Params**: `status: Optional[str] = Query("active")` (default filters active devices).
   - **Response**: `{"code": 0, "data": List[schemas.DeviceTokenResponse]}`.

3. **`DELETE /api/device/revoke/{device_id}`**
   - **Auth**: Requires standard user authentication.
   - **Path Parameter**: `device_id: int`.
   - **Response**: `{"code": 0, "message": "Device token revoked successfully", "data": {"id": device_id, "status": "revoked"}}`.
   - **Error**: 404 if device token not found for current user.

4. **`GET /api/device/verify`** (Verification Test Endpoint)
   - **Auth**: Uses `get_current_device_token` dependency (`X-Device-Token` header).
   - **Response**: `{"code": 0, "status": "valid", "device_name": device.device_name, "user_id": device.user_id}`.

---

### 3.5 App Main Integration (`Back/app/main.py`)
Register the device router in `Back/app/main.py`:
```python
from .routers import device
...
app.include_router(device.router, prefix="/api/device", tags=["Device Management"])
```

---

## 4. Verification Plan

1. **Model & Schema Imports Verification**:
   - Run python check: `python3 -c "from app.models import DeviceToken; from app.schemas import DeviceTokenResponse"`
2. **Database Table Creation Verification**:
   - Execute seed script or backend start, verify table `device_tokens` exists in SQLite DB schema (`sqlite3 db.sqlite3 ".schema device_tokens"`).
3. **Endpoint Functional Verification**:
   - Pair device token via `POST /api/device/pair-token` with user JWT token.
   - Verify active device list via `GET /api/device/list`.
   - Test device authentication via `X-Device-Token` header on `/api/device/verify`.
   - Revoke device token via `DELETE /api/device/revoke/{device_id}` and verify subsequent authentication attempts return HTTP 403 Forbidden.

---
*Report prepared by Explorer 1 for Milestone 2 implementation.*
