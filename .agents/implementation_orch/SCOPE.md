# Scope: Implementation Track

## Architecture
- Backend: FastAPI API server in `/home/xasanboy/ERP/Back` interacting with database via SQLAlchemy ORM.
- Reference Backend: Laravel application in `/home/xasanboy/Knittix-new` representing expected schema and capabilities.
- Frontend: Vue/Vite client in `/home/xasanboy/ERP/Front` displaying Cutting Orders with overlapping avatar rows for responsible users.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Backend Verification & Parity | Support responsible_user_ids in list and save endpoints; verify other core modules (Salary, Workers, Products). | None | DONE |
| 2 | Frontend Add/Edit Dialogue | Multi-select user dropdown fetching from /api/user/list in Cutting.vue. | None | DONE |
| 3 | Frontend Avatar Stack | Implement circular overlapping avatars with tooltip on hover with negative margin overlap. | M1 | DONE |
| 4 | Phase 1: E2E Test Pass | Pass 100% of E2E tests (Tiers 1-4) sequentially once TEST_READY.md is published. | M1, M2, M3 | DONE |
| 5 | Phase 2: Adversarial Coverage Hardening | Run adversarial testing (Tier 5) on the implementation with Challenger, Worker, Reviewer cycle. | M4 | IN_PROGRESS |

## Interface Contracts
### Frontend ↔ Backend (Cutting Orders)
- GET `/cutting/order/list` -> returns JSON with code 0 and data list. Each item should serialize `responsible_user_ids: list[str]`.
- POST `/cutting/order/save` -> accepts JSON matching `CuttingOrderCreate` schema. Supports `responsible_user_ids: list[str]`.
- GET `/user/list` -> returns list of users to populate dropdown.

## Code Layout
- Frontend views: `/home/xasanboy/ERP/Front/src/views/Cutting/Cutting.vue`
- Frontend components: `/home/xasanboy/ERP/Front/src/components/Avatars/src/Avatars.vue`
- Backend routers: `/home/xasanboy/ERP/Back/app/routers/cutting.py`
- Backend models: `/home/xasanboy/ERP/Back/app/models.py`
- Backend schemas: `/home/xasanboy/ERP/Back/app/schemas.py`
- Backend CRUD: `/home/xasanboy/ERP/Back/app/crud.py`
