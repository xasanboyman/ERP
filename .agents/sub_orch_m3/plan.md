# Plan — Milestone 3: Frontend Personal Center Connected Devices UI (R1)

## Overview
Implement the "Connected Devices" section in Personal Center UI (`Front/src/views/Personal/PersonalCenter.vue` or equivalent), enabling device pairing token generation (`POST /api/device/pair-token`), rendering QR codes for device pairing, querying connected devices list (`GET /api/device/list`), and device revocation (`DELETE /api/device/revoke/{device_id}`).

## Steps
1. **Exploration**:
   - Spawn 3 Explorers (`teamwork_preview_explorer`) to investigate existing `PersonalCenter.vue` or personal views, check API client/setup, existing libraries (QR code library, canvas, icon usage, Vue 3 / Element Plus / Ant Design / Tailwind or whatever UI framework is used in `Front`), check existing API routes, mock data or backend setup, test infrastructure, build and test commands for `Front`.
2. **Implementation**:
   - Spawn 1 Worker (`teamwork_preview_worker`) with the findings from Explorers to implement the Connected Devices section, QR code rendering, API integration (`pair-token`, `device/list`, `revoke`), error handling, UI state management, and test suite/verification.
3. **Review & Challenge**:
   - Spawn 2 Reviewers (`teamwork_preview_reviewer`) to independently review implementation quality, API correctness, QR rendering, token revocation UI updates, unit tests, and layout conformance.
   - Spawn 2 Challengers (`teamwork_preview_challenger`) to empirically test functionality, edge cases, error conditions, invalid token invalidation, and UI rendering.
4. **Audit**:
   - Spawn 1 Forensic Auditor (`teamwork_preview_auditor`) to perform integrity verification and verify no hardcoding/facades.
5. **Gate & Handoff**:
   - Evaluate gate criteria. If clean, mark milestone complete, create `handoff.md`, and notify parent orchestrator via `send_message`.
