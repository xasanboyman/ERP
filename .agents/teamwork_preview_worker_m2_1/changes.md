# Summary of Code Changes for Milestone 2 (R1)

## 1. Database Model (`Back/app/models.py`)
- Created `DeviceToken` SQLAlchemy model mapping to `device_tokens` table:
  - `id`: Integer primary key (indexed, autoincrements)
  - `user_id`: Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
  - `device_name`: String, nullable=False
  - `token`: String, unique=True, index=True, nullable=False
  - `status`: String, default="active", nullable=False
  - `created_at`: DateTime, default=datetime.datetime.utcnow
  - `last_used_at`: DateTime, nullable=True
  - `user`: Relationship to `User` with backref `"device_tokens"`

## 2. Schemas (`Back/app/schemas.py`)
- Defined Pydantic models:
  - `DevicePairRequest`: `device_name: str`
  - `DevicePairTokenResponse`: `token: str`, `qr_payload: str`, `device_name: str`, `created_at: datetime`
  - `DeviceTokenOut`: `id: int`, `user_id: int`, `device_name: str`, `token: str`, `status: str`, `created_at: datetime`, `last_used_at: datetime | None`, with `from_attributes = True`
  - `DeviceTokenListResponse`: `total: int`, `list: List[DeviceTokenOut]`

## 3. CRUD Functions (`Back/app/crud.py`)
- Implemented core CRUD helpers:
  - `create_device_token(db, user_id, device_name)`: generates `devtok_<urlsafe_32>` token string, sets status="active", created_at, commits & refreshes.
  - `get_user_device_tokens(db, user_id, status=None)`: fetches all or filtered device tokens for a user.
  - `get_device_token_by_token(db, token)`: retrieves DeviceToken by token string.
  - `get_device_token_by_id(db, device_id, user_id=None)`: retrieves DeviceToken by id (and optionally user_id).
  - `revoke_device_token(db, device_id, user_id=None)`: updates status to "revoked", commits & refreshes.
  - `update_device_token_last_used(db, device_token)`: updates `last_used_at` to current UTC timestamp.

## 4. Auth Dependency (`Back/app/auth.py`)
- Implemented `get_current_device_token` dependency:
  - Header alias: `X-Device-Token`
  - Returns 401 if missing header or token not in DB or user not found.
  - Returns 403 if status is "revoked" or inactive.
  - Throttled update of `last_used_at` if `last_used_at` is None or > 60 seconds ago.

## 5. Device Router & Main App Integration (`Back/app/routers/device.py` & `Back/app/main.py`)
- Created `/api/device/` API endpoints:
  - `POST /api/device/pair-token`: pairs new device, returns token & QR code JSON string payload.
  - `GET /api/device/list`: returns list of user devices.
  - `DELETE /api/device/revoke/{device_id}`: revokes device token for current user.
  - `GET /api/device/verify`: protected verification endpoint using `get_current_device_token`.
- Registered `device.router` in `Back/app/main.py`.

## 6. Unit & Integration Tests (`Back/tests/test_device.py`)
- Implemented test suite covering lifecycle of CRUD operations, API endpoints, header validation, token revocation, error status codes (401/403/404), and `last_used_at` throttling.
