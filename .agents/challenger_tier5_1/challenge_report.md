# Adversarial Challenge Report

## Challenge Summary

**Overall risk assessment**: HIGH

Through white-box source code analysis and targeted E2E adversarial testing, we identified critical vulnerabilities and logic flaws in the FastAPI backend's handling of database integrity, input validation, and transaction idempotency.

---

## Challenges

### [High] Challenge 1: Lack of SQLite Foreign Key Enforcement
- **Assumption challenged**: Deleting a parent entity (e.g., `Worker`) will cascade-delete or set null on child records referencing it (e.g., `Salary`), and creating child records referencing nonexistent parent entities (e.g., `Product`, `CuttingProcess`) will fail.
- **Attack scenario**: 
  1. A worker is created and assigned a pending salary payout.
  2. The worker is deleted via `/worker/delete`.
  3. The salary record remains in `salaries` referring to the deleted worker ID (dangling reference).
  4. Similarly, orders can be created via `/cutting/order/save` referencing invalid `productId` values.
- **Blast radius**: Database corruption, broken relational integrity, and frontend crashes when displaying records with empty/invalid relations.
- **Mitigation**: Enable SQLite foreign key constraints at connection startup in SQLAlchemy by setting an event listener:
  ```python
  from sqlalchemy.engine import Engine
  from sqlalchemy import event

  @event.listens_for(Engine, "connect")
  def set_sqlite_pragma(dbapi_connection, connection_record):
      cursor = dbapi_connection.cursor()
      cursor.execute("PRAGMA foreign_keys=ON")
      cursor.close()
  ```

### [High] Challenge 2: Non-Idempotent QR Scan Execution (Double Scan/Replay)
- **Assumption challenged**: Scanning a QR code to assign a worker is an idempotent action that only records a single task execution up to the QR code's quantity.
- **Attack scenario**: 
  1. A worker scans a QR code to record task execution via `/qr/assign-worker`.
  2. The worker (or an automated script) repeats the request multiple times with the same code.
  3. The backend creates a new `CuttingTaskExecution` record for *each* scan request without checking if the QR has already been scanned/completed.
- **Blast radius**: Wage theft or inflated payroll expenses due to duplicated execution quantities; tasks are marked completed with incorrect log history.
- **Mitigation**: Verify that `qr.status` is not already `"scanned"` (or check for existing executions linked to the QR code) before calling `create_cutting_task_execution`.

### [Medium] Challenge 3: Missing Boundary Validation for Item Quantity
- **Assumption challenged**: Frontend inputs are trusted, and order quantities are always positive integers.
- **Attack scenario**:
  1. A client submits a payload to `/cutting/order/save` containing negative quantities (e.g., `quantity: -500`).
  2. The order is saved successfully.
  3. When starting production, tasks are created with negative quantities, allowing any positive execution to immediately complete the tasks.
- **Blast radius**: Invalid inventory counts, negative workload logs, and corrupted analytics summaries.
- **Mitigation**: Add validation constraints (e.g., `Field(..., gt=0)`) to `quantity` fields in `CuttingOrderItemCreate` and `CuttingTaskExecutionCreate` schemas.

### [Medium] Challenge 4: Missing Completeness Checks on Production Start
- **Assumption challenged**: Orders containing no items cannot progress to production.
- **Attack scenario**:
  1. An order is created with an empty items list `[]`.
  2. The client calls `/cutting/order/start-production`.
  3. The status transitions to `"in_production"`, but no tasks are generated, leaving the order permanently stuck in progress.
- **Blast radius**: Stuck processes and dead state representations in the workflow pipeline.
- **Mitigation**: Validate that `db_order.items` is not empty before allowing the production start transition.

---

## Stress Test Results

- **QR Replay Attack** → Expected: Reject double scans/duplicate executions → Actual: Accepted double scans, creating duplicate task executions → **FAIL**
- **Foreign Key Cascade (Worker -> Salary)** → Expected: Salary record deleted when worker is deleted → Actual: Salary record remained pointing to deleted worker ID → **FAIL**
- **Foreign Key Enforcement (Product ID)** → Expected: Reject order creation with nonexistent product ID → Actual: Accepted order referencing invalid product ID → **FAIL**
- **Negative Item Quantity** → Expected: Reject negative quantity in order items → Actual: Saved order successfully with quantity `-500` → **FAIL**
- **Production Start on Empty Order** → Expected: Reject production start for empty order → Actual: Transitioned status to `in_production` with no tasks → **FAIL**

---

## Unchallenged Areas

- **AI Assistant Routing** — Out of scope.
- **Frontend Circular Avatar Layout** — Focused on backend API vulnerabilities, frontend CSS layout not tested.
