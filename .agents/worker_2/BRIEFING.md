# BRIEFING — 2026-07-07T02:06:00Z

## Mission
Implement input validation and database integrity checks in the FastAPI backend to resolve the 12 adversarial test failures.

## 🔒 My Identity
- Archetype: teamwork_preview_worker
- Roles: implementer, qa, specialist
- Working directory: /home/xasanboy/ERP/.agents/worker_2
- Original parent: 9078f2e9-a7ae-4100-b7ef-3bbf55ac6da8
- Milestone: backend_validation_integrity

## 🔒 Key Constraints
- CODE_ONLY network mode: no external website or service access, no curl/wget/lynx.
- No cheating: all implementations must be genuine, no hardcoding, no dummy/facade implementations.
- Write only to our own folder /home/xasanboy/ERP/.agents/worker_2 for agent metadata.
- Perform minimal changes following code modification rules.

## Current Parent
- Conversation ID: 9078f2e9-a7ae-4100-b7ef-3bbf55ac6da8
- Updated: not yet

## Task Summary
- **What to build**: Input validation and database integrity checks in the FastAPI backend.
  1. QR Code Replay Protection in `/qr/assign-worker` (reject worker assignment if status is "scanned").
  2. Worker Deletion Salary Cascade in `delete_worker` (manually delete any Salary records referencing workerId first).
  3. Database Integrity & Validation for Cutting Orders in `create_cutting_order` and `start_production_for_order`. Also wrap calls in `/cutting/order/save` and `/cutting/order/start-production` routes with ValueError catch to return HTTP 400.
  4. QR Code quantity bounds in `/qr/save` (validate quantity > 0 and <= task.quantity).
  5. Salary worker validation in `/salary/save` (verify workerId corresponds to existing worker).
  6. Referenced stage deletion cleanup in `/cutting/stage/delete` (set stageId to None for tasks referencing the stage ID before deletion).
- **Success criteria**: 62 E2E tests pass and 12 adversarial tests pass.
- **Interface contracts**: API endpoints in `/home/xasanboy/ERP/Back/app`
- **Code layout**: FastAPI architecture (routers, crud, models, etc.)

## Key Decisions Made
- [TBD]

## Artifact Index
- [TBD]

## Change Tracker
- **Files modified**: [None]
- **Build status**: Untested
- **Pending issues**: None

## Quality Status
- **Build/test result**: Untested
- **Lint status**: Untested
- **Tests added/modified**: None

## Loaded Skills
- **Source**: None
- **Local copy**: None
- **Core methodology**: None
