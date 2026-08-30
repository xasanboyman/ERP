# Plan: Milestone 4 — Backend Sales Push & Mobile Checkout API (R2 & R3)

## Objective
Implement backend DB models, schemas, CRUD operations, and FastAPI router endpoints for:
1. Computer Sale Push (`/api/sales/push-pc-sale`, `/api/sales/pending-pushes`, `/api/sales/respond-push`, `/api/sales/push-payload/{push_id}`).
2. Mobile Standalone Checkout (`/api/sales/phone-checkout`).
3. Enforce strict device token security (`get_current_device_token` from `Back/app/auth.py`).

## Iteration Loop Steps
1. **Explorer Phase**: Dispatch 3 Explorers to investigate current codebase (`Back/app/routers/`, `Back/app/models.py` or DB models, `Back/app/auth.py`, `Back/app/schemas.py`, test suite) and design implementation plan.
2. **Worker Phase**: Dispatch 1 Worker to implement DB models, schemas, CRUD, router endpoints, and unit tests.
3. **Reviewer Phase**: Dispatch 2 Reviewers independently to verify code quality, API compliance, device token security, and test suite execution.
4. **Challenger Phase**: Dispatch 2 Challengers to perform empirical verification and stress testing.
5. **Auditor Phase**: Dispatch 1 Forensic Auditor (`teamwork_preview_auditor`) to verify zero integrity violations.
6. **Gate & Synthesis**: Synthesize all reports, verify pass criteria, write `handoff.md`, and report completion to parent.
