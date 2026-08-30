# Scope: E2E Testing Track

## Architecture
- Backend: FastAPI API server under `/home/xasanboy/ERP/Back`
- Frontend: Vue/Vite client under `/home/xasanboy/ERP/Front`
- Reference Laravel Backend: `/home/xasanboy/Knittix-new`
- E2E Test Suite: To be constructed independently, requirement-driven, opaque-box.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Exploration & Feature Inventory | Analyze backend router files, frontend views, and reference Laravel application to build full feature checklist. | None | DONE |
| 2 | Test Infra & Runner Setup | Create test runner script, verify endpoint availability, choose testing libraries (e.g. pytest/playwright/requests). | M1 | DONE |
| 3 | Tier 1-4 Test Case Implementation | Implement feature coverage (T1), boundary cases (T2), combinations (T3), and workloads (T4). | M2 | DONE |
| 4 | Audit & Documentation | Run Forensic Auditor, write TEST_INFRA.md and TEST_READY.md. | M3 | PLANNED |
| 5 | Resolve Department Facade | Fix facade user save/delete endpoints in department.py router, integrate with db/seeder. | M3 | IN_PROGRESS |

## Interface Contracts
- GET `/cutting/order/list` -> returns JSON with code 0 and data list. Each item should serialize `responsible_user_ids: list[str]`.
- POST `/cutting/order/save` -> accepts JSON matching `CuttingOrderCreate` schema. Supports `responsible_user_ids: list[str]`.
- GET `/api/user/list` or `/user/list` -> list of users for dropdown.
- Parity endpoints (checking other modules' endpoints for parity against reference).

## Code Layout
- Test Suite: `/home/xasanboy/ERP/tests/e2e` (to be created)
