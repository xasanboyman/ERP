# Dispatch Log

## 2026-09-15T17:44:00Z

You are the Project Orchestrator for the multi-tenant ERP hardening project.

Your Working Directory: /home/xasanboy/ERP/.agents/orchestrator
Project Workspace: /home/xasanboy/ERP
Authoritative Request: /home/xasanboy/ERP/.agents/ORIGINAL_REQUEST.md

User Request:
Use a very large team of agents.
Harden, complete, and verify the multi-tenant ERP system at /home/xasanboy/ERP, ensuring full company data isolation, flawless Super Admin control over company accounts, Oracle VPS backend synchronization, and a modern icon-driven UI.

Working directory: /home/xasanboy/ERP
Integrity mode: development

Requirements:
- R1. Multi-Tenancy Hardening and Data Isolation: All backend endpoints (products, sales, warehouse, analytics, workers, users) must strictly enforce tenant isolation (company_id). No company admin or regular user may view or modify another company's records. The dynamic route tree (GET /api/role/list) must automatically determine user permissions from the Authorization: Bearer <token> header, returning only the standard modules (/dashboard, /product, /sales, /hr) for normal and company admin accounts, strictly omitting /company. Any non-superadmin attempt to navigate to #/company or #/company/list must be blocked and redirected to /404.
- R2. Super Admin Account & Subscription Management: Super Admin (admin) manages company accounts, subscription tiers, and system credentials, rather than directly managing worker employees of individual companies. Super Admin must be able to create new companies with initial admin credentials, reset passwords or update logins for any company admin account, toggle company statuses, and upgrade plans (Basic vs Pro). The Super Admin dashboard and drilldown drawer must present high-level aggregate metrics (worker counts, product counts, revenue, debt) while keeping individual worker records read-only for monitoring purposes.
- R3. Modern UI Standards & Zero-Emoji Enforcement: The entire ERP frontend must strictly adhere to professional enterprise standards, utilizing Element Plus and Iconify SVG icons (vi-ep:* / ep:*) and eliminating all raw Unicode emojis. Modals, drawers, and status indicators must provide responsive feedback, clear validation, and consistent styling across dark and light modes.
- R4. Automated Testing and Oracle VPS Deployment: A comprehensive automated test suite must execute against the live API, validating authentication for Super Admin (admin), company admins, and regular users, verifying role-based menu structures, testing password reset workflows, and verifying data isolation between tenants. All backend updates must be synchronized to the Oracle VPS (139.185.55.147) and verified against the production PostgreSQL instance (erp_db) without disturbing other running services.

Acceptance Criteria:
- Multi-Tenancy & Routing:
  - Regular users and company admins receive only /dashboard, /product, /sales, /hr from GET /api/role/list with Bearer auth (no roleName query parameter).
  - Non-superadmin access to #/company or #/company/list is blocked and redirects to /404.
  - Cross-tenant data leakage is prevented: querying products, sales, or workers returns only records belonging to the authenticated user's company.
- Super Admin & Account Control:
  - Super Admin can create a new company with custom login credentials, and the new company admin can log in immediately.
  - Super Admin can reset any company admin's password; login with old credentials fails and login with new credentials succeeds.
  - Drilldown drawer displays company overview, admin account details, and aggregate metrics (worker count, products count, revenue, debt) with workers in read-only mode.
- UI & Icon Quality:
  - Zero emojis remain in the Company Management views, dialogs, and navigation menus; all visual indicators use ep:* icons.
  - Responsive drawer and dialogs operate cleanly with loading states, error handling, and Element Plus message notifications.
- Build & Deployment:
  - npm run build in Front/ completes successfully without TypeScript or build errors.
  - Backend code is synchronized to Oracle VPS (139.185.55.147) and erp-backend.service is running and healthy.

Responsibilities:
1. Initialize your BRIEFING.md, plan.md, and progress.md in your working directory /home/xasanboy/ERP/.agents/orchestrator.
2. Decompose the mission into milestones/tracks and deploy specialized subagents into dedicated directories under /home/xasanboy/ERP/.agents/.
3. Continuously update your progress.md.
4. When all tasks and verification steps are complete, send a final completion report to the Sentinel with full evidence chains.
