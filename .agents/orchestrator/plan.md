# Project Orchestration Plan: Multi-Tenant ERP Hardening

## Overview
Hardening, completion, and end-to-end verification of the multi-tenant ERP system at `/home/xasanboy/ERP` based on requirements R1-R4:
- R1: Multi-Tenancy Hardening and Data Isolation (company_id filtering across all tables/endpoints, dynamic role route security without `roleName` query param leak, non-superadmin blocking of #/company to /404).
- R2: Super Admin Account & Subscription Management (Company creation with initial credentials, password reset/login updates, plan toggle Basic vs Pro, high-level aggregate metrics in drilldown drawer with read-only workers).
- R3: Modern UI Standards & Zero-Emoji Enforcement (Iconify `vi-ep:*`/`ep:*` replacement, removal of raw Unicode emojis in views/dialogs/menus, dark/light mode consistency, responsive drawers).
- R4: Automated Testing & Oracle VPS Deployment (Comprehensive automated test suite executing against live API, synchronization of backend to Oracle VPS 139.185.55.147, erp-backend.service verification without disturbing existing services).

## Tracks & Phases

### Phase 0: System Survey (Current)
- Dispatch 3 parallel Explorers:
  - `teamwork_preview_explorer` (Backend): Inspect backend routes, middleware, company_id handling, auth, `/api/role/list`, company admin endpoints.
  - `teamwork_preview_explorer` (Frontend): Inspect frontend routing guards, menu generation, `#company` views, emoji occurrences, Element Plus components.
  - `teamwork_preview_explorer` (DevOps & Test): Inspect current test scripts, VPS deployment scripts, SSH access, database schema, migration status.
- Synthesize into `/home/xasanboy/ERP/PROJECT.md` with Feature Inventory, Architecture, and Milestone decomposition.

### Phase 1: Dual Track Execution
#### Track A: E2E Testing Orchestration (`sub_orch_e2e`)
- Design opaque-box test infrastructure (`TEST_INFRA.md`).
- Implement 4-tier test suite (Feature coverage, boundaries, pairwise combinations, real-world workloads).
- Produce `TEST_READY.md`.

#### Track B: Implementation Track
- Milestone 1: Multi-Tenancy & Dynamic Route Hardening.
- Milestone 2: Super Admin Management & Read-Only Worker Drilldown.
- Milestone 3: Modern UI & Zero-Emoji Standardization.
- Milestone 4: Oracle VPS Sync & Live Service Health Check.
- Milestone 5: Full E2E Test Suite Execution (Pass 100%) + Adversarial Hardening (Tier 5).

### Phase 2: Final Gate & Forensic Integrity Audit
- Verify every milestone gate with Reviewers, Challengers, and Forensic Auditor (`teamwork_preview_auditor`).
- Send final completion report with full evidence chains to Sentinel.
