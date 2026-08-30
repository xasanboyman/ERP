# Original User Request

## Initial Request — 2026-07-07T06:48:11+05:00

You are the E2E Testing Orchestrator (`e2e_testing_orch`). Your working directory is `/home/xasanboy/ERP/.agents/e2e_testing_orch`.
Your parent is the Project Orchestrator (`9078f2e9-a7ae-4100-b7ef-3bbf55ac6da8`).

Your mission is to execute the E2E Testing Track for the project.
1. Design and write a comprehensive, requirement-driven, opaque-box test suite for backend APIs (checking list/save of cutting orders with `responsible_user_ids`, verifying other modules' endpoints for parity) and frontend behavior.
2. The test suite must cover:
   - Tier 1: Feature Coverage (>=5 tests per feature).
   - Tier 2: Boundary & Corner Cases (>=5 tests per feature).
   - Tier 3: Cross-Feature Combinations (pairwise coverage).
   - Tier 4: Real-World Application Scenarios (>=5 workloads).
3. Set up a test runner and structure the tests independently of implementation internals. Since we are in CODE_ONLY network mode, the test suite should run on the local machine against local endpoints.
4. Document the test architecture in `TEST_INFRA.md` at the project root.
5. Create all necessary test scripts and cases, run them, and ensure the test infra itself runs correctly.
6. Once complete, publish `TEST_READY.md` at the project root following the format in instructions.
7. Report completion and test instructions back to the Project Orchestrator.
