## 2026-07-07T01:50:55Z
Role: E2E Test Suite Developer & QA Worker
Working directory: /home/xasanboy/ERP/.agents/teamwork_preview_worker_impl
Task:
You must design, implement, run, and document the E2E test suite for the ERP application.

### MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

### Scope of Tests:
1. Features to test:
   - **Feature 1 (User / Auth Module)**: Login endpoint, fetch user list, check user roles/active statuses.
   - **Feature 2 (Cutting Orders Module)**: Create order, list orders, verify `responsible_user_ids` is persisted and returned properly as a JSON array of strings, delete orders, and start production.
   - **Feature 3 (Worker Module)**: Create workers, update workers, list workers, verify unique 6-digit `employee_code` generation, delete workers.
   - **Feature 4 (Product Module)**: CRUD for products (create, update, list, details, delete).
   - **Feature 5 (QR Code Module)**: Generate QR code (ULID format), update status, list QR codes, check metadata, assign worker.

2. Test Coverage Tiers:
   - **Tier 1 (Feature Coverage)**: At least 5 happy-path test cases per feature (25 total).
   - **Tier 2 (Boundary & Corner Cases)**: At least 5 boundary/validation error cases per feature (25 total). Check invalid schemas, empty inputs, non-existent references, edge/boundary limits, wrong status transitions.
   - **Tier 3 (Cross-Feature Combinations)**: At least 5 pairwise test cases showing interaction between features (e.g. creating a product/users, using them in a cutting order, creating a QR code, scanning it, checking worker task assignment).
   - **Tier 4 (Real-World Application Scenarios)**: At least 5 workload scenarios:
     - Workload 1: Product creation -> Cutting Order Setup -> Assign responsible users -> Start Production -> Generate QR -> Scan QR -> Assign worker -> Complete production.
     - Workload 2: Multi-user assignment and overlapping avatar validation on frontend API parity.
     - Workload 3: Worker onboarding -> Employee code generation -> QR scan task execution -> Salary/Payout analytics verification.
     - Workload 4: Validation error recovery: post invalid payloads, verify graceful API error code (code != 0), submit correct payload, save, and check cascading order status.
     - Workload 5: Audit trail and analytics validation: verify activity logs and analytics endpoints reflect user actions sequentially.

3. Framework & Execution:
   - Create the tests under `/home/xasanboy/ERP/tests/e2e`. Use Pytest as the test runner, combined with `requests` for API tests, and `playwright` (if available/installable) or python-based simulated UI interactions/E2E assertions.
   - Setup a script `/home/xasanboy/ERP/run_e2e_tests.sh` to run the entire test suite, starting the backend and frontend servers locally if not already running, executing the tests, and returning a clean exit code.
   - Run the tests to ensure the test suite executes successfully and all tests pass.

4. Documentation:
   - Document the test architecture in `TEST_INFRA.md` at the project root.
   - Publish `TEST_READY.md` at the project root following the format in the instructions.
   - Write a detailed handoff report in `/home/xasanboy/ERP/.agents/teamwork_preview_worker_impl/handoff.md` showing pytest execution output.
   - When complete, call send_message to report to parent.
