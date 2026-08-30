# Scope: Milestone 2 — Backend Device Token Management & Verification API

## Mission
Implement backend database models, migrations/schema initialization, CRUD functions, authentication dependencies/middleware, and API endpoints for device pairing, token authorization, and device revocation (Requirement R1).

## Requirements & Functionality
- **DB Model (`DeviceToken`)**:
  - `id`: Integer primary key (or string UUID/ULID)
  - `user_id`: Integer foreign key -> User
  - `device_name`: String
  - `token`: Unique String (secure token)
  - `status`: String ("active", "revoked")
  - `created_at`, `last_used_at`: Datetime
- **API Endpoints**:
  - `POST /api/device/pair-token` (requires user auth): Generates a new device pairing token and QR code payload string for logged-in user.
  - `GET /api/device/list` (requires user auth): Lists all active & connected devices for current user.
  - `DELETE /api/device/revoke/{device_id}` (requires user auth): Revokes device token (sets status="revoked" or deletes record from DB).
- **Security & Authorization Middleware**:
  - `get_current_device_token`: FastAPI dependency parsing `X-Device-Token` header.
  - Validates token exists in DB, is active, and is tied to a valid user.
  - Returns 401/403 Forbidden if missing, invalid, or revoked.

## Code Files
- Models: `/home/xasanboy/ERP/Back/app/models.py`
- Schemas: `/home/xasanboy/ERP/Back/app/schemas.py`
- CRUD: `/home/xasanboy/ERP/Back/app/crud.py`
- Router: `/home/xasanboy/ERP/Back/app/routers/device.py`
- Main app inclusion: `/home/xasanboy/ERP/Back/app/main.py`
- Seed script updates if necessary: `/home/xasanboy/ERP/Back/seed.py`
