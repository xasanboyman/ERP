# Handoff Report — Adversarial Verification (Tier 5)

## 1. Observation

We directly observed that when running the newly added adversarial tests located in `/home/xasanboy/ERP/tests/e2e/test_erp_adversarial_1.py`, they failed, exposing severe security, logic, and database integrity vulnerabilities in the FastAPI backend:
1. **Replay Scan Attack**: The test `test_adversarial_qr_replay` failed because the backend allowed scanning a QR code twice, returning `code = 0` (success) for both scans and duplicating the executions.
   ```
   tests/e2e/test_erp_adversarial_1.py:71: AssertionError
   >       assert res_scan2.json()["code"] != 0, "Security/Business logic failure: Allowed QR replay/double scan!"
   E       AssertionError: Security/Business logic failure: Allowed QR replay/double scan!
   E       assert 0 != 0
   ```
2. **Foreign Key Cascade Failure**: The test `test_adversarial_deleted_worker_cascades` failed because after deleting a worker, their associated salary record remained in the database with a dangling `workerId`.
   ```
   tests/e2e/test_erp_adversarial_1.py:107: AssertionError
   >       assert len(worker_salaries) == 0, "Database integrity failure: Salary record was NOT deleted when worker was deleted (dangling foreign key)!"
   E       AssertionError: Database integrity failure: Salary record was NOT deleted when worker was deleted (dangling foreign key)!
   E       assert 1 == 0
   ```
3. **Missing Foreign Key Check on Save**: The test `test_adversarial_nonexistent_product_fk` failed because the backend allowed saving an order item referencing a nonexistent product.
   ```
   tests/e2e/test_erp_adversarial_1.py:120: AssertionError
   >       assert res.status_code in [400, 422] or res.json()["code"] != 0, "Database integrity failure: Allowed order item referencing nonexistent product!"
   E       AssertionError: Database integrity failure: Allowed order item referencing nonexistent product!
   E       assert (200 in [400, 422] or 0 != 0)
   ```
4. **Missing Negative Quantity Validation**: The test `test_adversarial_negative_quantity_order` failed because the backend accepted order item quantities of `-500` and returned status code 200.
   ```
   tests/e2e/test_erp_adversarial_1.py:133: AssertionError
   >       assert res.status_code in [400, 422] or res.json().get("code", 0) != 0, "Business logic failure: Allowed order creation with negative quantity!"
   E       AssertionError: Business logic failure: Allowed order creation with negative quantity!
   E       assert (200 in [400, 422] or 0 != 0)
   ```
5. **Production Start on Empty Order**: The test `test_adversarial_empty_items_production` failed because starting production on an order with 0 items succeeded.
   ```
   tests/e2e/test_erp_adversarial_1.py:154: AssertionError
   >           assert res_start.status_code in [400, 422] or res_start.json().get("code", 0) != 0, "Business logic failure: Started production on an order with empty items list!"
   E           AssertionError: Business logic failure: Started production on an order with empty items list!
   E           assert (200 in [400, 422] or 0 != 0)
   ```

We verified the layout compliance:
- Source code directories analyzed: `/home/xasanboy/ERP/Back/app`, `/home/xasanboy/ERP/Front/src/views/Cutting/Cutting.vue`
- Existing tests: `/home/xasanboy/ERP/tests/e2e/test_erp_e2e.py`
- Added adversarial tests: `/home/xasanboy/ERP/tests/e2e/test_erp_adversarial_1.py`
- Agent metadata is correctly confined to the absolute path `/home/xasanboy/ERP/.agents/challenger_tier5_1`. No code, tests, or application database files are placed in `.agents/`.

---

## 2. Logic Chain

1. Source inspection of `Back/app/database.py` shows that the SQLite engine does not run `PRAGMA foreign_keys = ON;` upon connection initialization.
2. Source inspection of `Back/app/models.py` shows relational tables (e.g. `salaries`, `cutting_order_items`) define standard SQL foreign key columns (`workerId`, `productId`).
3. Since SQLite has foreign key constraints disabled by default, the database accepts invalid foreign references (such as nonexistent product IDs in `cutting_order_items`) and fails to execute `ON DELETE CASCADE` actions (leaving salary records orphaned when workers are deleted).
4. Source inspection of `Back/app/routers/qr.py` at `/qr/assign-worker` shows it creates a new task execution directly via `crud.create_cutting_task_execution` without inspecting if `qr.status == "scanned"`. Therefore, executing the endpoint repeatedly creates duplicate wage execution logs.
5. Source inspection of `Back/app/schemas.py` shows `quantity: int` fields do not have constraints preventing negative or zero inputs, leading to logic exploitation in order placement and execution tracking.

---

## 3. Caveats

- We did not implement fixes for the vulnerabilities, as per instructions restricting review agents to verification and challenge roles only.
- We did not perform dynamic frontend testing using Playwright, as UI elements could not be interactively booted without headful Xvfb displays and were out of scope.
- Database locks or high concurrent request loads (e.g., locking behavior under stress) were not simulated.

---

## 4. Conclusion

The application backend contains five critical validation and database integrity vulnerabilities. Relational cascades do not operate as expected, inputs are insufficiently validated for boundary values (such as negative numbers), and transaction endpoints are not idempotent against duplicate QR code scan actions.

---

## 5. Verification Method

To reproduce the findings and verify the exposed gaps, perform the following:
1. Boot the FastAPI backend server on port 8000.
2. Execute the adversarial test suite manually using Pytest:
   ```bash
   ./Back/venv/bin/pytest tests/e2e/test_erp_adversarial_1.py -v
   ```
3. Observe that 5 tests are collected and 5 assertion failures occur, corresponding to the vulnerabilities outlined above.
