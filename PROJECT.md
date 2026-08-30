# Project: Mobile QR/Barcode Scanning System & Dual POS Handover for ERP

## Architecture
- **Backend**: FastAPI API server in `/home/xasanboy/ERP/Back` with SQLAlchemy ORM and SQLite database (`erp.db`).
- **Frontend**: Vue 3 client in `/home/xasanboy/ERP/Front` (Personal Center, Sales POS, Mobile Scanner).
- **Security & Pairing**: Per-device access tokens stored in SQLite DB (`DeviceToken`), tied to logged-in user accounts, validated via FastAPI auth dependency (`get_current_device_token`) for mobile endpoints. Device revocation destroys DB token record.
- **Real-Time Notification & Handover**: Sales Push notification channel (WebSocket / Polling API) sending Accept/Decline alerts to PC active session, pre-filling POS cart at `/sales/pos` upon acceptance.
- **Mobile POS Terminal**: Standalone phone scanner view with dual modes (Computer Sale vs Phone Sale).

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | E2E Testing Track | Requirement-driven opaque-box test suite (Tiers 1-4) in `tests/e2e/test_mobile_pos_e2e.py`. Publish `TEST_READY.md`. | None | IN_PROGRESS |
| 2 | Backend Device Token Management | DB schema (`DeviceToken`), token generation, revocation endpoints, auth dependency. | None | DONE |
| 3 | Frontend Personal Center Connected Devices | UI in `PersonalCenter.vue` with QR generator for pairing and device revocation management. | M2 | IN_PROGRESS |
| 4 | Backend Sales Push & Mobile Checkout API | PC Push alert payload handler, pending alert status, accept/decline endpoints, mobile direct checkout. | M2 | IN_PROGRESS |
| 5 | Frontend Mobile Dual Sales & PC POS Alert | Mobile scanner dual-mode UI (PC sale vs Phone POS), global PC Accept/Decline alert modal, handover to `/sales/pos`. | M3, M4 | PLANNED |
| 6 | E2E Verification & Hardening | Phase 1: Pass 100% E2E tests (Tiers 1-4). Phase 2: Tier 5 adversarial testing & Forensic Audit verification. | M1, M2, M3, M4, M5 | PLANNED |

## Interface Contracts

### Device Management (R1)
- `POST /api/device/pair-token` -> `{ user_id, device_name }` returns `{ pair_code, token, expires_at }`
- `GET /api/device/list` -> returns list of connected devices for current user
- `DELETE /api/device/revoke/{device_id}` -> invalidates and destroys device token in DB
- Request Header `X-Device-Token: <token>` -> validated on mobile scanner endpoints. Revoked/invalid token returns `401 Unauthorized` / `403 Forbidden`.

### Sales Push & Real-Time Alert (R2/R3)
- `POST /api/sales/push-pc-sale` -> `{ device_token, items: [{ product_id, quantity, price }], pc_user_id }` returns `{ push_id, status: "pending" }`
- `GET /api/sales/pending-pushes` -> returns list of active pending push alerts for active PC user session
- `POST /api/sales/respond-push` -> `{ push_id, action: "accept" | "decline" }` returns `{ push_id, status }`
- `GET /api/sales/push-payload/{push_id}` -> returns full item list & quantity details for pre-filling `/sales/pos`

### Mobile Standalone POS Checkout (R2)
- `POST /api/sales/phone-checkout` -> `{ device_token, items: [{ product_id, quantity, price }], payment_type: "cash" | "card" | "debt", total_amount, paid_amount }` returns sale transaction record.

## Code Layout
- Backend Models: `/home/xasanboy/ERP/Back/app/models.py`
- Backend Schemas: `/home/xasanboy/ERP/Back/app/schemas.py`
- Backend Routers: `/home/xasanboy/ERP/Back/app/routers/device.py`, `sales.py`
- Backend Auth/Middleware: `/home/xasanboy/ERP/Back/app/auth.py`
- Frontend Personal Center: `/home/xasanboy/ERP/Front/src/views/Personal/PersonalCenter.vue` (or equivalent)
- Frontend Mobile Scanner: `/home/xasanboy/ERP/Front/src/views/Mobile/MobileScanner.vue`
- Frontend POS View: `/home/xasanboy/ERP/Front/src/views/Sales/Pos.vue`
- Frontend Alert Modal: `/home/xasanboy/ERP/Front/src/components/PosPushAlertModal.vue`
