# Analysis Report: Backend Device Token Management & Verification API (R1) — Security Dependency Design

**Explorer ID**: Explorer 2 (Milestone 2)  
**Working Directory**: `/home/xasanboy/ERP/.agents/teamwork_preview_explorer_m2_2`  
**Scope Document**: `/home/xasanboy/ERP/.agents/sub_orch_m2/SCOPE.md`  
**Target Workspace**: `/home/xasanboy/ERP`  
**Date**: 2026-08-09  

---

## 1. Overview & Objective

This report details the architectural investigation of authentication mechanisms in the backend of the ERP system (`/home/xasanboy/ERP/Back/app/`) and provides a complete, robust design for the `get_current_device_token` security dependency required for Requirement R1.

The primary goals of this dependency are:
1. Extract and parse the `X-Device-Token` HTTP header from incoming API requests.
2. Query the database for a matching `DeviceToken` record.
3. Validate that the token exists, its status is `'active'` (not `'revoked'` or `'inactive'`), and its associated `User` is valid.
4. Enforce appropriate HTTP status codes:
   - `401 Unauthorized` for missing headers, unrecognized tokens, or missing users.
   - `403 Forbidden` for revoked or non-active tokens.
5. Manage and update the `last_used_at` timestamp safely and efficiently.

---

## 2. Existing Authentication Mechanisms in Backend

### 2.1 Codebase Audit of Security Modules

An audit of `/home/xasanboy/ERP/Back/app/` revealed the following current authentication structure:

- **JWT Creation & Decoding**:
  - `app/routers/auth.py` contains `create_access_token` and `decode_access_token` using PyJWT with `SECRET_KEY = "super-secret-key-that-is-hard-to-guess"` and `ALGORITHM = "HS256"`.
  - Tokens expire after 12 hours (`exp: datetime.datetime.utcnow() + timedelta(hours=12)`).

- **User Authentication Dependencies**:
  - `get_current_user_required` (`app/routers/crm.py` lines 32–44):
    - Extract header: `authorization: str = Header(None)`
    - Decodes token using `decode_access_token(authorization)`.
    - Queries DB: `db.query(models.User).filter(models.User.username == payload["sub"]).first()`
    - Raises `HTTPException(status_code=401, detail="...")` if token is invalid or user is not found.
  - `get_current_user_optional` (`app/routers/crm.py` lines 24–30):
    - Returns `None` instead of raising exceptions when authorization is missing or invalid.
  - `get_current_user_from_header` (`app/routers/role.py` lines 19–25):
    - Re-implements user lookup from `Authorization` header.

- **Token Expiration Middleware**:
  - In `app/main.py` (lines 102–112), `token_expiration_middleware` inspects `Authorization` headers on incoming requests and returns a `401` JSON response if token decoding fails or expires.

### 2.2 Key Insights & Design Implications

1. **Header Parameter Handling**:
   - Current dependencies use `authorization: str = Header(None)` where FastAPI automatically binds `Authorization` header.
   - For custom header `X-Device-Token`, specifying `x_device_token: str | None = Header(None, alias="X-Device-Token")` ensures precise case-insensitive extraction according to HTTP standard.

2. **Session Dependency Injection**:
   - Dependencies consume `db: Session = Depends(get_db)` from `app.database`, ensuring a shared database session per request lifecycle.

3. **Separation of User Auth vs. Device Auth**:
   - User Auth relies on JWT tokens passed in `Authorization: Bearer <jwt>`.
   - Device Auth relies on persistent opaque tokens stored in `DeviceToken` DB table passed in `X-Device-Token: <token>`.
   - Creating `get_current_device_token` (and derivative `get_current_device_user`) allows endpoints (such as POS terminal actions or QR verification) to authenticate hardware devices directly.

---

## 3. Detailed Design of `get_current_device_token` Dependency

### 3.1 Function Signature & Header Extraction

```python
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app import models

def get_current_device_token(
    x_device_token: str | None = Header(None, alias="X-Device-Token"),
    db: Session = Depends(get_db)
) -> models.DeviceToken:
```

### 3.2 Verification Flow & Error Rules

1. **Step 1: Check Header Presence**
   - If `x_device_token` is missing or empty `""`:
   - **Status Code**: `401 Unauthorized`
   - **Detail**: `"Unauthorized: Missing X-Device-Token header"`

2. **Step 2: Database Token Lookup**
   - Query: `db.query(models.DeviceToken).filter(models.DeviceToken.token == x_device_token).first()`
   - If `device_token` is `None`:
   - **Status Code**: `401 Unauthorized`
   - **Detail**: `"Unauthorized: Invalid device token"`

3. **Step 3: Verify Token Status**
   - If `device_token.status == "revoked"`:
     - **Status Code**: `403 Forbidden`
     - **Detail**: `"Forbidden: Device token has been revoked"`
   - If `device_token.status != "active"`:
     - **Status Code**: `403 Forbidden`
     - **Detail**: `"Forbidden: Device token is inactive"`

4. **Step 4: Verify Associated User Validity**
   - Query: `db.query(models.User).filter(models.User.id == device_token.user_id).first()`
   - If user is `None`:
     - **Status Code**: `401 Unauthorized`
     - **Detail**: `"Unauthorized: User associated with device token not found"`

5. **Step 5: Update `last_used_at` Timestamp**
   - Update `device_token.last_used_at` (see Strategy analysis in Section 4).
   - Commit session or rely on request session flush.

6. **Step 6: Return ORM Object**
   - Return validated `device_token` instance.

---

## 4. Analysis & Strategies for Handling `last_used_at`

Updating `last_used_at` on every authenticated request is necessary for device management auditability, but can introduce database write overhead if executed naively.

### 4.1 Comparison of Implementation Options

| Strategy | Mechanism | Pros | Cons | Recommendation |
|---|---|---|---|---|
| **A. Immediate Synchronous Update** | `device_token.last_used_at = now; db.commit()` on every request | Simple, exact timestamp precision | High DB write load for frequent polling | Suitable for low-frequency endpoints |
| **B. Throttled Synchronous Update** | Only update if `last_used_at` is `None` or updated `> N` seconds ago (e.g. 60s) | Reduces DB writes by ~99%, thread-safe, no extra background tasks | Timestamp precision lagged by up to 60s | **RECOMMENDED DEFAULT** |
| **C. FastAPI BackgroundTask Update** | Offloads update to `BackgroundTasks.add_task` | Does not block request response | Requires creating a separate DB session in task thread; potential lock issues in SQLite | Secondary choice |

### 4.2 Recommended Throttled Update Pattern (Strategy B Code Example)

```python
UPDATE_INTERVAL_SECONDS = 60

now = datetime.now(timezone.utc)
should_update = False

if device_token.last_used_at is None:
    should_update = True
else:
    try:
        if isinstance(device_token.last_used_at, datetime):
            last_dt = device_token.last_used_at
        else:
            last_dt = datetime.fromisoformat(str(device_token.last_used_at))
        
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
            
        if (now - last_dt).total_seconds() >= UPDATE_INTERVAL_SECONDS:
            should_update = True
    except Exception:
        should_update = True

if should_update:
    device_token.last_used_at = now
    db.add(device_token)
    db.commit()
    db.refresh(device_token)
```

---

## 5. Derivative & Helper Dependencies

To simplify route handlers requiring both device token and user information, we recommend defining helper dependencies alongside `get_current_device_token`:

### 5.1 `get_current_device_user`

```python
def get_current_device_user(
    device_token: models.DeviceToken = Depends(get_current_device_token),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency for endpoints requiring the authenticated User operating via an active Device.
    """
    user = db.query(models.User).filter(models.User.id == device_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: User associated with device token not found"
        )
    return user
```

### 5.2 Combined Device Context Tuple `(DeviceToken, User)`

```python
def get_device_auth_context(
    device_token: models.DeviceToken = Depends(get_current_device_token),
    db: Session = Depends(get_db)
) -> tuple[models.DeviceToken, models.User]:
    """
    Dependency providing both DeviceToken and User objects to route handlers.
    """
    user = db.query(models.User).filter(models.User.id == device_token.user_id).first()
    return device_token, user
```

---

## 6. Implementation Placement Recommendation

We recommend placing the new dependencies in a central location:
- Either `/home/xasanboy/ERP/Back/app/auth.py` (creating a clean, unified security dependency file).
- Or in `/home/xasanboy/ERP/Back/app/routers/device.py` if restricted to device domain, and re-exporting in `app/auth.py`.

Creating `/home/xasanboy/ERP/Back/app/auth.py` as a standalone security module will also allow clean refactoring of JWT dependencies (`get_current_user_required`, etc.) in future milestones.

---

## 7. Verification Method

Once implemented by Implementer agents, the dependency can be independently verified via pytest unit tests or `curl`:

1. **Valid Token Test**:
   `curl -H "X-Device-Token: <valid_active_token>" http://localhost:8000/api/device/list` -> Expected HTTP `200 OK`.
2. **Missing Token Test**:
   `curl http://localhost:8000/api/device/list` -> Expected HTTP `401 Unauthorized` (`"Missing X-Device-Token header"`).
3. **Invalid Token Test**:
   `curl -H "X-Device-Token: non_existent_token_123" http://localhost:8000/api/device/list` -> Expected HTTP `401 Unauthorized` (`"Invalid device token"`).
4. **Revoked Token Test**:
   `curl -H "X-Device-Token: <revoked_token>" http://localhost:8000/api/device/list` -> Expected HTTP `403 Forbidden` (`"Device token has been revoked"`).
5. **`last_used_at` Timestamp Verification**:
   Inspect DB `device_tokens` table after request to confirm `last_used_at` updated.
