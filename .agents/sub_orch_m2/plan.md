# Plan — Milestone 2: Backend Device Token Management & Verification API

## Objective
Implement backend device token management and verification API (Requirement R1) in Back/app:
1. `DeviceToken` SQLAlchemy DB model in `Back/app/models.py`.
2. Pydantic schemas in `Back/app/schemas.py`.
3. CRUD methods in `Back/app/crud.py`.
4. API endpoints in `Back/app/routers/device.py` (`POST /api/device/pair-token`, `GET /api/device/list`, `DELETE /api/device/revoke/{device_id}`). Include route in `Back/app/main.py`.
5. Device token authentication dependency (`get_current_device_token` parsing `X-Device-Token`) in `Back/app/auth.py` returning 401/403 for invalid/revoked tokens.
6. Seed updates if needed in `Back/seed.py`.

## Execution Plan & Workflow Protocol
- Step 1: Initialize metadata files and heartbeat cron.
- Step 2: Spawn 3 parallel Explorers (`teamwork_preview_explorer`) to analyze existing codebase, existing models, auth dependencies, router conventions, and test setups for Back/app.
- Step 3: Aggregate Explorer findings and prepare implementation instructions for Worker (`teamwork_preview_worker`).
- Step 4: Dispatch Worker to implement code changes, update seed/db migrations if needed, run pytest/tests, and document results.
- Step 5: Spawn 2 parallel Reviewers (`teamwork_preview_reviewer`) to independently review implementation quality, security, and edge cases.
- Step 6: Spawn 2 parallel Challengers (`teamwork_preview_challenger`) to stress-test endpoints and authentication rules.
- Step 7: Spawn Forensic Auditor (`teamwork_preview_auditor`) to verify zero integrity violations / no hardcoding.
- Step 8: Gate evaluation. If all pass -> finalize handoff.md and send message to parent. If any fails -> iterate back to Explorer/Worker with audit evidence.
