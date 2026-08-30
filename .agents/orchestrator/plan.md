# Project Execution Plan: Mobile QR/Barcode Scanning & Dual POS Handover

## Overview
This plan outlines the milestones, delegation topology, verification steps, and execution strategy for the Mobile QR/Barcode scanning system for ERP.

## Milestones & Timeline

### Milestone 1: E2E Testing Track & Infrastructure
- **Owner**: E2E Testing Orchestrator (Sub-Orchestrator)
- **Objective**: Build comprehensive requirement-driven test suite (`tests/e2e/test_mobile_pos_e2e.py`) and update `TEST_INFRA.md` & `TEST_READY.md`.
- **Tiers**:
  - Tier 1: Feature Coverage (Device pairing, token auth, PC push, Mobile checkout)
  - Tier 2: Boundary & Edge Cases (Revoked tokens, invalid amounts, declining push, duplicate pairings)
  - Tier 3: Cross-Feature Workflows (Device pair -> Mobile scan -> PC Push -> Accept -> POS checkout)
  - Tier 4: Real-World Application Scenarios (Full multi-device POS lifecycle)
- **Deliverable**: `TEST_READY.md` published with passing test commands.

### Milestone 2: Backend Device Token Management & Verification (R1)
- **Owner**: Sub-Orchestrator (Backend Team)
- **Objective**: Implement DB models (`DeviceToken`), token generator, revocation endpoints, and token validation dependency in FastAPI.
- **Verification**: Unit & integration tests for token CRUD and middleware rejection of revoked tokens.

### Milestone 3: Frontend Personal Center Connected Devices UI (R1)
- **Owner**: Sub-Orchestrator (Frontend Team)
- **Objective**: Implement "Connected Devices" section in `PersonalCenter.vue` with QR code generation for pairing and device revocation management.
- **Verification**: UI component verification, QR generation test, revocation UI trigger.

### Milestone 4: Backend Sales Push & Mobile Checkout API (R2 & R3)
- **Owner**: Sub-Orchestrator (Backend Team)
- **Objective**: Implement real-time push notification endpoints (PC sale push, pending push query, accept/decline response, payload fetch) and mobile checkout endpoint.
- **Verification**: Backend API test execution for push payload lifecycle.

### Milestone 5: Frontend Mobile Dual Sales & PC POS Handover (R2 & R3)
- **Owner**: Sub-Orchestrator (Frontend Team)
- **Objective**: Implement `MobileScanner.vue` with Computer Sale Mode vs Phone Sale Mode, and global `PosPushAlertModal.vue` on PC navigating to `/sales/pos`.
- **Verification**: Frontend flow verification and simulated user handover.

### Milestone 6: E2E Verification & Hardening
- **Owner**: Project Orchestrator / Challenger / Auditor
- **Phase 1**: Run E2E test suite (Tiers 1-4) until 100% pass.
- **Phase 2**: Adversarial whitebox testing (Tier 5) + Forensic Integrity Audit (`teamwork_preview_auditor`).

## Verification Protocols
- All subagents must run and document build & test commands in `handoff.md`.
- Forensic auditor verdict MUST be CLEAN for completion.
