# Plan: Milestone 1 — E2E Testing Track

## Objective
Design and implement a complete, requirement-driven, opaque-box E2E test suite in `tests/e2e/test_mobile_pos_e2e.py` and runner script `run_e2e_tests.sh`, document in `TEST_INFRA.md`, and publish `TEST_READY.md`.

## Key Requirements & Tiers
- **Requirements**:
  - R1: Device Pairing, Token Authorization & Revocation (Personal Center)
  - R2: Mobile Dual Sales Modes (Computer Sale Mode vs Phone Sale Mode)
  - R3: PC POS Notification & Handover (Accept/Decline modal and `/sales/pos` cart population)
- **Tiers**:
  - Tier 1: Feature Coverage (>=5 tests per feature)
  - Tier 2: Boundary & Corner Cases (>=5 tests per feature)
  - Tier 3: Cross-Feature Combinations (pairwise integration flows)
  - Tier 4: Real-World Application Scenarios & Workloads

## Step-by-Step Workflow

### Iteration Loop 1:
1. **Explorer Phase**: Dispatch 3 Explorers to analyze backend API endpoints, database setup, environment requirements, pytest harness setup, and draft complete test architecture.
2. **Worker Phase**: Dispatch Worker to write `tests/e2e/test_mobile_pos_e2e.py`, `run_e2e_tests.sh`, `TEST_INFRA.md`, and publish `TEST_READY.md`. Worker must execute test suite and verify pass.
3. **Reviewer Phase**: Dispatch 2 Reviewers independently to verify code quality, requirement coverage across Tiers 1-4, test runner execution, and absence of hardcoded assertions or dummy implementations.
4. **Challenger Phase**: Dispatch 2 Challengers to stress test and empirically verify tests, verifying genuine HTTP client requests and edge case handling.
5. **Forensic Audit Phase**: Dispatch Forensic Auditor to check for integrity, ensuring no cheating/mocking/facade implementations exist.
6. **Gate Evaluation**: Evaluate worker results, reviewer approvals, challenger reports, and auditor verdict (BINARY VETO).
7. **Handoff**: Produce `handoff.md` and notify parent.
