# Original User Request

## 2026-08-09T05:02:38Z

Implement a secure Mobile QR/Barcode scanning system for ERP with connected device token management in Personal Center, dual-mode sales (Mobile POS vs PC POS Push with Accept/Decline alert), and full transaction capabilities.

Working directory: /home/xasanboy/ERP
Integrity mode: development

## Requirements

### R1. Device Pairing, Token Authorization & Management (Personal Center)
- In http://localhost:4000/#/personal/personal-center, add a "Connected Devices" section with a QR code generator for device pairing.
- Store per-device access tokens tied to logged-in user account with strict backend role/permission checking for every scan request.
- Provide device revocation in Personal Center that destroys the token in DB. Invalid/revoked tokens redirect mobile scanner to re-pairing.

### R2. Mobile Dual Sales Modes (PC Sale vs Phone Sale)
- When opening mobile scanner view, provide 2 choices:
  - **Computer Sale Mode**: Scans items & amounts on phone, sends alert to PC.
  - **Phone Sale Mode**: Complete standalone POS terminal on phone (scanning, quantity, full/debt payments, cash/card).

### R3. PC POS Notification & Handover (`/sales/pos` — Yangi Sotuv)
- When "Computer Sale" is triggered from phone, send a real-time alert (Accept/Decline modal) to the PC.
- Upon pressing "Accept" on PC, automatically navigate/open http://localhost:4000/#/sales/pos (Yangi Sotuv / POS Kassa), pre-fill scanned items & quantities, allowing the cashier to continue editing/finalizing sale.

## Acceptance Criteria

### Security & Device Pairing
- [ ] Device token generated on PC personal center can be scanned and saved on mobile.
- [ ] Backend blocks requests from revoked or unauthenticated device tokens with forbidden status.
- [ ] Revoking a device in Personal Center invalidates it immediately on mobile.

### PC Sale Alert & Handover
- [ ] Scanned items from phone trigger Accept/Decline pop-up alert on active PC session.
- [ ] Pressing Accept opens /sales/pos (Yangi Sotuv) with all scanned items and amounts populated.
- [ ] Pressing Decline cancels the payload transfer and alerts phone.

### Mobile POS Terminal
- [ ] Phone Sale mode enables full POS workflow directly on mobile (scanning, amount input, debt/cash/card checkout).

## 2026-09-15T17:38:18Z

Use a very large team of agents.
Harden, complete, and verify the multi-tenant ERP system at /home/xasanboy/ERP, ensuring full company data isolation, flawless Super Admin control over company accounts, Oracle VPS backend synchronization, and a modern icon-driven UI.

Working directory: /home/xasanboy/ERP
Integrity mode: development

## Requirements

### R1. Multi-Tenancy Hardening and Data Isolation
All backend endpoints (products, sales, warehouse, analytics, workers, users) must strictly enforce tenant isolation (`company_id`). No company admin or regular user may view or modify another company's records. The dynamic route tree (`GET /api/role/list`) must automatically determine user permissions from the `Authorization: Bearer <token>` header, returning only the standard modules (`/dashboard`, `/product`, `/sales`, `/hr`) for normal and company admin accounts, strictly omitting `/company`. Any non-superadmin attempt to navigate to `#/company` or `#/company/list` must be blocked and redirected to `/404`.

### R2. Super Admin Account & Subscription Management
Super Admin (`admin`) manages company accounts, subscription tiers, and system credentials, rather than directly managing worker employees of individual companies. Super Admin must be able to create new companies with initial admin credentials, reset passwords or update logins for any company admin account, toggle company statuses, and upgrade plans (Basic vs Pro). The Super Admin dashboard and drilldown drawer must present high-level aggregate metrics (worker counts, product counts, revenue, debt) while keeping individual worker records read-only for monitoring purposes.

### R3. Modern UI Standards & Zero-Emoji Enforcement
The entire ERP frontend must strictly adhere to professional enterprise standards, utilizing Element Plus and Iconify SVG icons (`vi-ep:*` / `ep:*`) and eliminating all raw Unicode emojis. Modals, drawers, and status indicators must provide responsive feedback, clear validation, and consistent styling across dark and light modes.

### R4. Automated Testing and Oracle VPS Deployment
A comprehensive automated test suite must execute against the live API, validating authentication for Super Admin (`admin`), company admins, and regular users, verifying role-based menu structures, testing password reset workflows, and verifying data isolation between tenants. All backend updates must be synchronized to the Oracle VPS (`139.185.55.147`) and verified against the production PostgreSQL instance (`erp_db`) without disturbing other running services.

## Acceptance Criteria

### Multi-Tenancy & Routing
- [ ] Regular users and company admins receive only `/dashboard`, `/product`, `/sales`, `/hr` from `GET /api/role/list` with Bearer auth (no `roleName` query parameter).
- [ ] Non-superadmin access to `#/company` or `#/company/list` is blocked and redirects to `/404`.
- [ ] Cross-tenant data leakage is prevented: querying products, sales, or workers returns only records belonging to the authenticated user's company.

### Super Admin & Account Control
- [ ] Super Admin can create a new company with custom login credentials, and the new company admin can log in immediately.
- [ ] Super Admin can reset any company admin's password; login with old credentials fails and login with new credentials succeeds.
- [ ] Drilldown drawer displays company overview, admin account details, and aggregate metrics (worker count, products count, revenue, debt) with workers in read-only mode.

### UI & Icon Quality
- [ ] Zero emojis remain in the Company Management views, dialogs, and navigation menus; all visual indicators use `ep:*` icons.
- [ ] Responsive drawer and dialogs operate cleanly with loading states, error handling, and Element Plus message notifications.

### Build & Deployment
- [ ] `npm run build` in `Front/` completes successfully without TypeScript or build errors.
- [ ] Backend code is synchronized to Oracle VPS (`139.185.55.147`) and `erp-backend.service` is running and healthy.


## 2026-09-15T18:34:51Z

Use a very large team of agents.
Execute an exhaustive, end-to-end multi-agent verification and audit across the entire ERP product at /home/xasanboy/ERP, dividing all functional domains into parallel verification tracks to guarantee that every single feature works correctly, with strict emphasis on role-based access control, tenant isolation, UI compliance, and production Oracle VPS stability.

Working directory: /home/xasanboy/ERP
Integrity mode: development

## Requirements

### R1. Role-Based Access Control & Route Security
Verify every role tier across the system:
- **Super Administrator** (`admin` on `comp-default`): Receives the full navigation tree (`/dashboard`, `/company`, `/product`, `/sales`, `/hr`, `/authorization`), full access to `#/company/list` and `#/company/main-account`.
- **Company Administrators** (`delta_admin`, `idk`, new companies): Receives strictly the 4 standard modules (`/dashboard`, `/product`, `/sales`, `/hr`) from `GET /api/role/list` with Bearer auth; `/company` is strictly omitted. Non-superadmin direct URL access to `#/company` or `#/company/list` is intercepted by the router guard and redirected to `/404`.
- **Standard Workers / Users** (`test`): Receives only standard modules; cannot view or access company management endpoints.
- Authentication tokens must be validated exclusively via `Authorization: Bearer <token>` without any query string parameter leakage.

### R2. End-to-End Multi-Tenant Isolation
Verify complete database and API isolation by `company_id`:
- Products, stock inventory, categories, and packaging belonging to one company are never visible or modifiable by another company or default user.
- Sales, POS terminal orders, customer records, and debt (`nasiya`) ledgers are strictly partitioned.
- Workers, departments, and payroll calculations are strictly scoped to the user's company.
- Analytics endpoints (monthly sales, dashboard totals, financial summaries) return metrics strictly for the authenticated tenant.

### R3. Super Admin Company & Account Administration
Verify Super Admin control boundaries:
- Super Admin can create new companies with designated admin credentials (`admin_username`, `admin_password`).
- Super Admin can reset any company admin's password and update login credentials via `POST /api/company/account/reset-password`; old passwords are confirmed invalidated and new passwords work immediately.
- Drilldown drawer displays company overview, admin account control, and aggregate business metrics (worker count, product count, total revenue, debt), keeping worker lists read-only without worker CRUD operations.
- Super Admin can upgrade company tiers (Basic vs Pro) and adjust expiration dates.

### R4. Frontend UI Polish, Zero-Emoji & Build Integrity
Verify UI standards across all views:
- Zero raw emojis in any view or component; all visual elements use official Element Plus or Iconify SVG icons (`ep:*` / `vi-ep:*`).
- All drawers, dialogs, and tables feature clean layout, clear feedback, and responsive styling.
- `npm run build` in `Front/` passes with zero compilation or TypeScript errors.

### R5. Production Oracle VPS & Database Stability
Verify live production synchronization:
- Backend code is synchronized to Oracle VPS (`139.185.55.147`) at `/home/ubuntu/erp-backend/app/`.
- `erp-backend.service` is active and healthy with zero systemd unit failures.
- PostgreSQL database (`erp_db`) sequences and tables are consistent with zero impact on other running services.

## Acceptance Criteria

### Role & Access Security
- [ ] `GET /api/role/list` with `admin` Bearer token returns full navigation tree including `/company`.
- [ ] `GET /api/role/list` with company admin (`delta_admin`, `idk`) or user (`test`) Bearer token returns strictly `['/dashboard', '/product', '/sales', '/hr']`.
- [ ] Direct browser URL navigation to `https://localhost:4000/#/company/list` as non-superadmin redirects to `/404`.
- [ ] Non-superadmin API requests to `/api/company/*` return HTTP 403 Forbidden or 404 Not Found.

### Tenant Data Isolation
- [ ] Product created under Company A is completely invisible in product search and listing under Company B.
- [ ] POS sale completed under Company A does not alter inventory or show in sales records of Company B.
- [ ] Customer debt recorded in Company A is not visible in Company B's debt ledger.

### Company Account Control
- [ ] Creating a company generates a functioning company admin account that can log in immediately.
- [ ] Password reset for a company admin succeeds; old password rejects login and new password authenticates with code 0.
- [ ] Drilldown drawer displays company metrics and admin credentials while keeping worker records in read-only mode.

### UI & Build Standards
- [ ] No raw Unicode emojis exist across Company, Dashboard, Product, Sales, and HR views.
- [ ] `npm run build` exits with code 0.

### Deployment & VPS Health
- [ ] `systemctl is-active erp-backend` on Oracle VPS returns `active`.
- [ ] `systemctl --failed` on Oracle VPS returns `0 loaded units listed`.
