## 2026-07-07T02:03:42Z

Implement database integrity, validation, and logic hardening on the FastAPI backend:
1. In `Back/app/database.py`, enable SQLite Foreign Key constraints using a SQLAlchemy Engine connection listener:
   ```python
   from sqlalchemy.engine import Engine
   from sqlalchemy import event

   @event.listens_for(Engine, "connect")
   def set_sqlite_pragma(dbapi_connection, connection_record):
       cursor = dbapi_connection.cursor()
       cursor.execute("PRAGMA foreign_keys=ON")
       cursor.close()
   ```
2. In `Back/app/models.py`, update the `stageId` ForeignKey in `CuttingTask` to have `ondelete="SET NULL"` and `nullable=True`.
3. In `Back/app/schemas.py`, add validation constraints `Field(..., gt=0)` to the `quantity` attribute of `CuttingOrderItemCreate` and `QrCodeCreate`.
4. In `Back/app/crud.py`, update `start_production_for_order` (where stages are parsed) to handle cases where a stage item in the stages list is a string/ID directly (e.g. `stage_id = stage_data`), or is a dictionary (e.g. `stage_id = stage_data.get("id") or stage_data.get("stageId")`), preventing unhandled `AttributeError` crashes.
5. In `Back/app/routers/cutting.py`:
   - In `/cutting/order/save`, validate that all usernames in `order_in.responsible_user_ids` exist in the database (returning a 400 error code if any do not), and deduplicate the list before saving.
   - In `/cutting/order/start-production`, verify that the order contains items (`order.items` is not empty), returning a 400 error code if it is empty.
6. In `Back/app/routers/qr.py`:
   - In `/qr/assign-worker`, check if `qr.status == "scanned"` and reject with a 400 error code if so.
   - In `/qr/save`, check if `qr_in.quantity > task.quantity` and reject with a 400 error code if it exceeds the task quantity.
7. In `Back/app/main.py`, register a global exception handler for SQLAlchemy `IntegrityError` to return a `JSONResponse` with status code 400 and code 400 to elegantly handle database constraint violations.
8. Execute both E2E tests and adversarial tests to verify success:
   ```bash
   cd /home/xasanboy/ERP
   ./run_e2e_tests.sh
   ./run_adversarial_tests.sh
   ```
   Ensure all tests pass cleanly.
9. Report changes, command output, and verification results in your handoff report inside `/home/xasanboy/ERP/.agents/worker_hardening_1`.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
