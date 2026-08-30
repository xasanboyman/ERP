# Scope: E2E Testing Track

## Mission
Design and implement a comprehensive, requirement-driven, opaque-box E2E test suite (`tests/e2e/test_mobile_pos_e2e.py` and test runner script `run_e2e_tests.sh`) for the Mobile QR/Barcode scanning system for ERP.

## Requirements Covered
- **R1**: Device Pairing, Token Authorization & Revocation (Personal Center)
- **R2**: Mobile Dual Sales Modes (Computer Sale Mode vs Phone Sale Mode)
- **R3**: PC POS Notification & Handover (Accept/Decline pop-up modal and `/sales/pos` cart population)

## Test Coverage Methodology & Tiers
- **Tier 1: Feature Coverage (>=5 tests per feature)**:
  - Device pair code generation & mobile registration
  - Valid token API requests authorization
  - Device token revocation from Personal Center
  - Mobile Computer Sale Mode push to PC
  - PC POS Accept alert & payload retrieval
  - PC POS Decline alert & cancellation
  - Mobile Phone Sale Mode checkout (Cash)
  - Mobile Phone Sale Mode checkout (Card)
  - Mobile Phone Sale Mode checkout (Debt)
- **Tier 2: Boundary & Corner Cases (>=5 tests per feature)**:
  - Unauthenticated requests without device token (401/403)
  - Requests with revoked device token (403 Forbidden)
  - Re-pairing after revocation
  - Computer Sale push with empty items list (validation failure)
  - Computer Sale push with invalid item IDs or negative quantities
  - Responding to nonexistent push ID
  - Responding twice to the same push ID
  - Mobile POS checkout with invalid amount or missing fields
- **Tier 3: Cross-Feature Combinations**:
  - Full flow: Pair device -> Scan items -> Push to PC -> Accept on PC -> Open POS -> Complete sale
  - Dual device pairing for single user account -> Revoke device 1 while device 2 remains active
- **Tier 4: Real-World Application Workloads**:
  - Multiple cashier sessions receiving distinct mobile push notifications
  - High-concurrency scanning & sales transactions

## Output Deliverables
- `/home/xasanboy/ERP/TEST_INFRA.md`: Full documentation of test architecture, setup, runner, and coverage tiers.
- `/home/xasanboy/ERP/TEST_READY.md`: Signal file published upon suite completion with run commands and coverage matrix.
- `/home/xasanboy/ERP/run_e2e_tests.sh`: Automated test runner script.
- `/home/xasanboy/ERP/tests/e2e/test_mobile_pos_e2e.py`: Complete pytest suite.
