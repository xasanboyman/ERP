## 2026-07-07T02:05:20Z

You are worker_2, a teamwork_preview_worker. Your working directory is `/home/xasanboy/ERP/.agents/worker_2`.
Your parent is the Project Orchestrator (`9078f2e9-a7ae-4100-b7ef-3bbf55ac6da8`).

Your mission is to implement input validation and database integrity checks in the FastAPI backend to resolve the 12 adversarial test failures reported by the auditor.

Please modify the backend code in `/home/xasanboy/ERP/Back/app` to implement the following validations and logic:
1. QR Code Replay Protection (in `Back/app/routers/qr.py`):
   - In `/qr/assign-worker`: Reject worker assignment if `qr.status == "scanned"`. Return `{"code": 400, "message": "QR Code already scanned/assigned"}`.
2. Worker Deletion Salary Cascade (in `Back/app/crud.py`):
   - In `delete_worker(db, worker_id)`: Manually delete any `Salary` records referencing the `worker_id` before deleting the worker:
     `db.query(models.Salary).filter(models.Salary.workerId == worker_id).delete()`
3. Database Integrity & Validation checks for Cutting Orders (in `Back/app/crud.py` and `Back/app/routers/cutting.py`):
   - In `create_cutting_order(db, order)`:
     - Deduplicate `responsible_user_ids` by mapping the list to unique items:
       `unique_user_ids = list(dict.fromkeys(order.responsible_user_ids or []))` and assign it to the order.
     - Validate that all responsible usernames exist in the `users` table:
       Query `models.User` by `username` for each username in `unique_user_ids`. If any do not exist, raise `ValueError`.
     - Validate that all `productId` in `order.items` exist in the `products` table:
       Query `models.Product` by `id` for each item. If any do not exist, raise `ValueError`.
     - Validate that all item quantities are greater than zero. If not, raise `ValueError`.
   - In `start_production_for_order(db, order_id)`:
     - Reject if `db_order.items` is empty by raising a `ValueError`.
     - Reject if any stage in `stages_list` is NOT a dictionary by raising a `ValueError`.
   - In `/cutting/order/save` and `/cutting/order/start-production` routes (in `Back/app/routers/cutting.py`):
     - Wrap the CRUD calls in `try...except ValueError as e` blocks and raise `HTTPException(status_code=400, detail=str(e))` if a `ValueError` is caught. Make sure to import `HTTPException` from `fastapi`.
4. QR Code quantity bounds (in `Back/app/routers/qr.py`):
   - In `/qr/save`: Validate that `qr_in.quantity > 0` and that `qr_in.quantity <= task.quantity`. If not, return `{"code": 400, "message": "Invalid quantity"}`.
5. Salary worker validation (in `Back/app/routers/salary.py`):
   - In `/salary/save`: Verify that `workerId` corresponds to an existing worker. If not, return `{"code": 404, "message": "Worker not found"}`.
6. Referenced stage deletion cleanup (in `Back/app/routers/cutting.py`):
   - In `/cutting/stage/delete`: Update all tasks referencing the stage ID being deleted to have `stageId = None` (or `stageId = ""`) before deleting the stage:
     `db.query(models.CuttingTask).filter(models.CuttingTask.stageId == i).update({models.CuttingTask.stageId: None})`

Run tests using `./run_e2e_tests.sh` and `./run_adversarial_tests.sh` (or using pytest in the backend virtualenv) to verify that all 62 E2E tests and all 12 adversarial tests pass successfully.
Write your implemented edits and verification logs in `/home/xasanboy/ERP/.agents/worker_2/handoff.md`.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
