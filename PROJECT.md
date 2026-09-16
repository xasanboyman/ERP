# Project: ERP Multi-Tenant Verification, Audit & Hardening

## Architecture
- **Backend**: FastAPI API server in `/home/xasanboy/ERP/Back/app/` with SQLAlchemy ORM, deployed on Oracle VPS `139.185.55.147` under systemd service `erp-backend.service`.
- **Database**: Production PostgreSQL `erp_db` hosted on Oracle VPS `139.185.55.147`, accessed locally via SSH port forwarding on `127.0.0.1:5433`.
- **Frontend**: Vue 3 / Vite enterprise application in `/home/xasanboy/ERP/Front/`, with Element Plus and Iconify SVG icons (`vi-ep:*` / `ep:*`), dynamic route tree from `GET /api/role/list`, and router permission guards in `Front/src/permission.ts`.
- **Reverse Proxy**: Nginx on Oracle VPS routing `^/(oracle/)?erp-api/(.*)$` to `127.0.0.1:8000/$2`, served publicly via HTTPS at `https://xn--dr8haa.uz/oracle/erp-api/`.
- **Local Dev Server**: Vite on `https://localhost:4000`, proxying `/api` requests to `https://xn--dr8haa.uz/oracle/erp-api/`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Strict Bearer Auth Header | Authenticate exclusively via `Authorization: Bearer <token>` without query string leakage | M1, M2 | survey |
| 2 | Dynamic Route RBAC Filtering | `GET /api/role/list` returns full navigation tree with `/company` for Super Admin, and strictly `['/dashboard', '/product', '/sales', '/hr']` for company admins/workers | M2 | survey |
| 3 | Frontend Route Guard Redirection | Direct navigation to `#/company` or `#/company/list` intercepted and redirected to `/404` for non-superadmins | M2 | survey |
| 4 | Company API Guarding | Non-superadmin access to `/api/company/*` returns HTTP 403 Forbidden or 404 | M2 | survey |
| 5 | Commerce Multi-Tenant Isolation | Strict `company_id` isolation across products, stock, categories, sales, POS, and nasiya ledgers | M2 | survey |
| 6 | HR & Worker Multi-Tenant Isolation | Eliminate cross-tenant leaks in `GET /worker/list` and `GET /salary/list` by enforcing `company_id` | M1, M2 | survey |
| 7 | Authentication Security Hardening | Remove hardcoded password bypass (`['123456', 'admin', '1234']`) in `auth.py` and `worker.py` | M1 | survey |
| 8 | Company Provisioning | Super Admin creates new company with custom credentials (`admin_username`, `admin_password`), immediate login | M3 | survey |
| 9 | Password Reset Workflow | `POST /api/company/account/reset-password`: invalidates old password and enables new password immediately | M1, M3 | survey |
| 10 | Company Drilldown Drawer | Display company overview, aggregate business metrics (workers, products, revenue, debt), and read-only worker table | M3 | survey |
| 11 | Company Plan & Expiration Control | Super Admin can upgrade company tiers (Basic vs Pro) and adjust expiration dates | M3 | survey |
| 12 | Zero-Emoji Enforcement | Zero raw Unicode emojis across Company, Dashboard, Product, Sales, and HR views; full `ep:*` / `vi-ep:*` SVG icon usage | M4 | survey |
| 13 | Frontend Build Integrity | `npm run build` in `Front/` executes cleanly with code 0 | M4 | survey |
| 14 | Production VPS Synchronization | Synchronize backend code to `/home/ubuntu/erp-backend/app/` on Oracle VPS `139.185.55.147` | M1, M5 | survey |
| 15 | VPS Systemd & DB Health | `systemctl is-active erp-backend` is active, `systemctl --failed` returns 0 failed units, `erp_db` consistent | M5 | survey |
| 16 | Adversarial & Forensic Verification | Stress-testing bypass attempts, SQL/tenant injection, and zero-tolerance forensic integrity audit | M6 | survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Backend Security Hardening & VPS Sync | Remove password backdoor in `auth.py:182` & `worker.py:83`, scope `GET /worker/list` & `GET /salary/list` by `company_id`, sync to VPS and restart `erp-backend.service`. | None | IN_PROGRESS |
| 2 | RBAC & Multi-Tenant Isolation Verification (R1, R2) | Verify Bearer auth, `GET /api/role/list` tree, router guard `/404` redirection, 403 API blocking, and cross-tenant product/sales/nasiya/worker isolation. | M1 | PLANNED |
| 3 | Super Admin Account & Subscription Control (R3) | Verify company creation, password reset (old fails, new succeeds), drilldown drawer metrics, read-only worker table, and tier upgrade. | M1 | PLANNED |
| 4 | Frontend UI Polish & Build Standards (R4) | Verify 0 raw emojis across views, SVG icon usage, drawer responsiveness, and `npm run build` exit code 0. | None | PLANNED |
| 5 | Production Oracle VPS & Database Stability (R5) | Verify Oracle VPS `139.185.55.147` service health (`active`), `systemctl --failed` (0 units), and database integrity without disturbing co-located services. | M1 | PLANNED |
| 6 | Adversarial Hardening & Forensic Integrity Audit | Dual Challenger stress-testing + Forensic Auditor zero-tolerance integrity audit. | M2, M3, M4, M5 | PLANNED |

## Interface Contracts
### Auth & Role Menu (R1)
- `POST /api/user/login` -> `{ username, password }` returns `{ code: 0, data: { token, is_super_admin, company_id, company_name } }`
- `GET /api/role/list` with Header `Authorization: Bearer <token>`:
  - For Super Admin (`is_super_admin: true`): returns routes including `['/dashboard', '/company', '/product', '/sales', '/hr', '/authorization']`
  - For Company Admin / Worker: returns strictly `['/dashboard', '/product', '/sales', '/hr']` (strictly omitting `/company`)

### Company Management (R3)
- `POST /api/company/save` (Super Admin only, Bearer token): `{ name, code, plan, billing_cycle, admin_username, admin_password, admin_full_name }`
- `POST /api/company/account/reset-password` (Super Admin only, Bearer token): `{ company_id, username, new_password }`
- `GET /api/company/drilldown/{company_id}` (Super Admin only, Bearer token): returns company overview, admin user credentials, metrics (product_count, worker_count, total_revenue, total_debt), and worker list (read-only)
- `POST /api/company/tier/upgrade` (Super Admin only, Bearer token): `{ company_id, plan, expires_at }`

### Multi-Tenant Data (R2)
- All endpoints (`/product/*`, `/sales/*`, `/worker/*`, `/salary/*`, `/analytics/*`):
  - Enforce `company_id` filtering extracted from the Bearer token
  - Client-supplied `company_id` parameter is strictly rejected or overridden for non-superadmins

## Code Layout
- Backend Models: `/home/xasanboy/ERP/Back/app/models.py`
- Backend CRUD: `/home/xasanboy/ERP/Back/app/crud.py`
- Backend Routers: `/home/xasanboy/ERP/Back/app/routers/` (`auth.py`, `user.py`, `role.py`, `company.py`, `product.py`, `sales.py`, `worker.py`, `salary.py`, `analytics.py`)
- Backend Auth: `/home/xasanboy/ERP/Back/app/auth.py`
- Frontend Router & Guards: `/home/xasanboy/ERP/Front/src/router/`, `Front/src/permission.ts`
- Frontend Views: `/home/xasanboy/ERP/Front/src/views/` (`Company/`, `Dashboard/`, `Product/`, `Sales/`, `HR/`)
- Test Suites: `/home/xasanboy/ERP/tests/` (`test_multi_tenant_lifecycle.py`, `verify_api.py`, `e2e/test_erp_e2e.py`, `e2e/test_erp_adversarial_*.py`)
- VPS Target: `ubuntu@139.185.55.147:/home/ubuntu/erp-backend/app/`
