# Test Specification Handoff Report — Explorer 2 (Milestone 1: E2E Testing Track)

**Working Directory**: `/home/xasanboy/ERP/.agents/explorer_e2e_2`  
**Date**: 2026-08-09  
**Target File**: `/home/xasanboy/ERP/.agents/explorer_e2e_2/handoff.md`  

---

## 1. Observation

Direct observations from examining the codebase, project architecture, and scope documentation:

### 1.1 Project Architecture & Files Inspected
- **`PROJECT.md`** (`/home/xasanboy/ERP/PROJECT.md`):
  - Architecture: FastAPI backend (`/home/xasanboy/ERP/Back`), SQLite database (`erp.db`), Vue 3 frontend (`/home/xasanboy/ERP/Front`).
  - Milestone 1 objective: Requirement-driven opaque-box E2E test suite in `tests/e2e/test_mobile_pos_e2e.py` and test runner `run_e2e_tests.sh`.
  - Interface contracts defined in lines 20–37 for R1 (Device Management), R2 (Mobile Sales / Phone POS), and R3 (Sales Push & Alert).
- **`SCOPE.md`** (`/home/xasanboy/ERP/.agents/sub_orch_e2e/SCOPE.md`):
  - Outlines 4 Tiers of testing: Tier 1 (Feature Coverage >=5 per feature), Tier 2 (Boundary & Corner Cases >=5 per feature), Tier 3 (Cross-Feature Combinations), Tier 4 (Real-World Application Workloads).
- **Backend Codebase** (`/home/xasanboy/ERP/Back/app`):
  - Database models (`models.py`): `User` (lines 17-30), `Product` (lines 61-79), `Sale` (lines 393-409), `SaleItem` (lines 413-426).
  - Existing sale router (`routers/sales.py`): `/sales/list` (lines 11-79) and `/sales/checkout` (lines 81-100+).
  - Auth module (`routers/auth.py`): JWT token structure `Bearer <token>` (lines 10-27, 82).

### 1.2 Verbatim Interface Contracts (from `PROJECT.md`)

```
### Device Management (R1)
- POST /api/device/pair-token -> { user_id, device_name } returns { pair_code, token, expires_at }
- GET /api/device/list -> returns list of connected devices for current user
- DELETE /api/device/revoke/{device_id} -> invalidates and destroys device token in DB
- Request Header X-Device-Token: <token> -> validated on mobile scanner endpoints. Revoked/invalid token returns 401 Unauthorized / 403 Forbidden.

### Sales Push & Real-Time Alert (R2/R3)
- POST /api/sales/push-pc-sale -> { device_token, items: [{ product_id, quantity, price }], pc_user_id } returns { push_id, status: "pending" }
- GET /api/sales/pending-pushes -> returns list of active pending push alerts for active PC user session
- POST /api/sales/respond-push -> { push_id, action: "accept" | "decline" } returns { push_id, status }
- GET /api/sales/push-payload/{push_id} -> returns full item list & quantity details for pre-filling /sales/pos

### Mobile Standalone POS Checkout (R2)
- POST /api/sales/phone-checkout -> { device_token, items: [{ product_id, quantity, price }], payment_type: "cash" | "card" | "debt", total_amount, paid_amount } returns sale transaction record.
```

---

## 2. Logic Chain

From the observed interface contracts, data models, and requirement specifications, the E2E test suite must validate end-to-end behavior across four distinct testing tiers. Each requirement (R1, R2, R3) is decomposed into explicit API calls, HTTP status codes, payload structures, database state assertions, and boundary conditions.

Below is the step-by-step mapping for all four tiers.

---

### Tier 1: Feature Coverage (>=5 per feature)

#### Feature R1: Device Pairing & Token Authorization
1. **`test_r1_t1_01_pair_code_generation`**
   - **Method & Endpoint**: `POST /api/device/pair-token`
   - **Headers**: `Authorization: Bearer <user_token>`
   - **Body**: `{"user_id": 1, "device_name": "Scanner-iPhone-14"}`
   - **Expected Status**: `200 OK` (or `201 Created`)
   - **Expected Response**: `{"pair_code": "<string_6chars>", "token": "<token_string>", "expires_at": "<ISO8601_timestamp>"}`
   - **DB Assertion**: Query `device_tokens` table where `user_id == 1` AND `device_name == 'Scanner-iPhone-14'`. Assert `is_active == 1` and `token` matches response.

2. **`test_r1_t1_02_device_list_retrieval`**
   - **Method & Endpoint**: `GET /api/device/list`
   - **Headers**: `Authorization: Bearer <user_token>`
   - **Expected Status**: `200 OK`
   - **Expected Response**: Array of device objects containing `id`, `device_name`, `expires_at`, `status`.
   - **DB Assertion**: Ensure array length equals count of active devices in `device_tokens` for the authenticated user.

3. **`test_r1_t1_03_valid_x_device_token_auth`**
   - **Method & Endpoint**: `POST /api/sales/push-pc-sale`
   - **Headers**: `X-Device-Token: <valid_device_token>`
   - **Body**: `{"device_token": "<valid_device_token>", "items": [{"product_id": "PROD-001", "quantity": 1, "price": 10.0}], "pc_user_id": 1}`
   - **Expected Status**: `200 OK`
   - **Expected Response**: `{"push_id": "<push_uuid>", "status": "pending"}`
   - **DB Assertion**: Check `sales_pushes` table for `push_id`, status `'pending'`.

4. **`test_r1_t1_04_device_revocation_from_personal_center`**
   - **Method & Endpoint**: `DELETE /api/device/revoke/{device_id}`
   - **Headers**: `Authorization: Bearer <user_token>`
   - **Path Param**: `{device_id}` (e.g. `DEV-1001`)
   - **Expected Status**: `200 OK`
   - **Expected Response**: `{"message": "Device token revoked", "device_id": "DEV-1001"}`
   - **DB Assertion**: `device_tokens` row `is_active` set to `0` or record status updated to `'revoked'`.

5. **`test_r1_t1_05_revoked_token_request_rejected`**
   - **Method & Endpoint**: `POST /api/sales/push-pc-sale`
   - **Headers**: `X-Device-Token: <revoked_device_token>`
   - **Body**: `{"device_token": "<revoked_device_token>", "items": [{"product_id": "PROD-001", "quantity": 1, "price": 10.0}], "pc_user_id": 1}`
   - **Expected Status**: `403 Forbidden` (or `401 Unauthorized`)
   - **Expected Response**: `{"detail": "Device token is revoked or invalid"}`
   - **DB Assertion**: Verify no new row inserted into `sales_pushes`.

---

#### Feature R2: Mobile Dual Sales Modes
1. **`test_r2_t1_01_computer_sale_mode_push_to_pc`**
   - **Method & Endpoint**: `POST /api/sales/push-pc-sale`
   - **Headers**: `X-Device-Token: <valid_device_token>`
   - **Body**: `{"device_token": "<token>", "items": [{"product_id": "PROD-001", "quantity": 3, "price": 25.0}], "pc_user_id": 1}`
   - **Expected Status**: `200 OK`
   - **Expected Response**: `{"push_id": "<push_id>", "status": "pending"}`
   - **DB Assertion**: `sales_pushes` row created with `pc_user_id=1`, `status='pending'`, payload contains 3 units of `PROD-001`.

2. **`test_r2_t1_02_phone_sale_checkout_cash`**
   - **Method & Endpoint**: `POST /api/sales/phone-checkout`
   - **Headers**: `X-Device-Token: <valid_device_token>`
   - **Body**: `{"device_token": "<token>", "items": [{"product_id": "PROD-001", "quantity": 2, "price": 15.0}], "payment_type": "cash", "total_amount": 30.0, "paid_amount": 30.0}`
   - **Expected Status**: `200 OK`
   - **Expected Response**: `{"id": "SALE-xxx", "receipt_number": "CHK-xxx", "payment_method": "naqd", "total_amount": 30.0, "paid_amount": 30.0, "debt_amount": 0.0}`
   - **DB Assertion**: `sales` row exists with `payment_method == 'naqd'`, `paid_amount == 30.0`. Product stock for `PROD-001` reduced by 2.

3. **`test_r2_t1_03_phone_sale_checkout_card`**
   - **Method & Endpoint**: `POST /api/sales/phone-checkout`
   - **Headers**: `X-Device-Token: <valid_device_token>`
   - **Body**: `{"device_token": "<token>", "items": [{"product_id": "PROD-002", "quantity": 1, "price": 50.0}], "payment_type": "card", "total_amount": 50.0, "paid_amount": 50.0}`
   - **Expected Status**: `200 OK`
   - **Expected Response**: `{"id": "SALE-xxx", "payment_method": "karta", "total_amount": 50.0, "paid_amount": 50.0, "debt_amount": 0.0}`
   - **DB Assertion**: `sales` record created with `payment_method == 'karta'`.

4. **`test_r2_t1_04_phone_sale_checkout_debt`**
   - **Method & Endpoint**: `POST /api/sales/phone-checkout`
   - **Headers**: `X-Device-Token: <valid_device_token>`
   - **Body**: `{"device_token": "<token>", "items": [{"product_id": "PROD-001", "quantity": 1, "price": 40.0}], "payment_type": "debt", "total_amount": 40.0, "paid_amount": 0.0}`
   - **Expected Status**: `200 OK`
   - **Expected Response**: `{"id": "SALE-xxx", "payment_method": "nasiya", "total_amount": 40.0, "paid_amount": 0.0, "debt_amount": 40.0}`
   - **DB Assertion**: `sales` record created with `payment_method == 'nasiya'` and `debt_amount == 40.0`.

5. **`test_r2_t1_05_phone_sale_multi_item_checkout`**
   - **Method & Endpoint**: `POST /api/sales/phone-checkout`
   - **Headers**: `X-Device-Token: <valid_device_token>`
   - **Body**: `{"device_token": "<token>", "items": [{"product_id": "PROD-001", "quantity": 2, "price": 10.0}, {"product_id": "PROD-002", "quantity": 1, "price": 20.0}], "payment_type": "cash", "total_amount": 40.0, "paid_amount": 40.0}`
   - **Expected Status**: `200 OK`
   - **Expected Response**: `{"id": "SALE-xxx", "total_items": 3, "total_amount": 40.0}`
   - **DB Assertion**: `sale_items` table contains 2 rows corresponding to `PROD-001` (qty 2) and `PROD-002` (qty 1).

---

#### Feature R3: PC POS Notification & Handover
1. **`test_r3_t1_01_get_pending_pushes_pc_session`**
   - **Method & Endpoint**: `GET /api/sales/pending-pushes`
   - **Headers**: `Authorization: Bearer <pc_user_token>`
   - **Expected Status**: `200 OK`
   - **Expected Response**: Array of pending push objects `[{"push_id": "<push_id>", "device_name": "Scanner-iPhone-14", "status": "pending", "item_count": 3}]`
   - **DB Assertion**: Matches count of rows in `sales_pushes` with `pc_user_id == <pc_user_id>` and `status == 'pending'`.

2. **`test_r3_t1_02_accept_push_alert`**
   - **Method & Endpoint**: `POST /api/sales/respond-push`
   - **Headers**: `Authorization: Bearer <pc_user_token>`
   - **Body**: `{"push_id": "<push_id>", "action": "accept"}`
   - **Expected Status**: `200 OK`
   - **Expected Response**: `{"push_id": "<push_id>", "status": "accepted"}`
   - **DB Assertion**: `sales_pushes` row `status` is updated to `'accepted'`.

3. **`test_r3_t1_03_decline_push_alert`**
   - **Method & Endpoint**: `POST /api/sales/respond-push`
   - **Headers**: `Authorization: Bearer <pc_user_token>`
   - **Body**: `{"push_id": "<push_id_2>", "action": "decline"}`
   - **Expected Status**: `200 OK`
   - **Expected Response**: `{"push_id": "<push_id_2>", "status": "declined"}`
   - **DB Assertion**: `sales_pushes` row `status` is updated to `'declined'`.

4. **`test_r3_t1_04_fetch_accepted_push_payload`**
   - **Method & Endpoint**: `GET /api/sales/push-payload/{push_id}`
   - **Headers**: `Authorization: Bearer <pc_user_token>`
   - **Path Param**: `{push_id}`
   - **Expected Status**: `200 OK`
   - **Expected Response**: `{"push_id": "<push_id>", "items": [{"product_id": "PROD-001", "product_name": "Product 1", "quantity": 3, "price": 25.0}], "total_amount": 75.0}`
   - **DB Assertion**: Payload items match original mobile push request payload.

5. **`test_r3_t1_05_complete_pos_checkout_after_handover`**
   - **Method & Endpoint**: `POST /api/sales/checkout`
   - **Headers**: `Authorization: Bearer <pc_user_token>`
   - **Body**: `{"items": [{"product_id": "PROD-001", "quantity": 3, "price": 25.0}], "payment_method": "naqd", "total_amount": 75.0, "paid_amount": 75.0, "customer_name": "Walk-in"}`
   - **Expected Status**: `200 OK`
   - **Expected Response**: `{"code": 0, "message": "Sotuv muvaffaqiyatli amalga oshirildi"}`
   - **DB Assertion**: `sales` row created, product stock for `PROD-001` decremented by 3.

---

### Tier 2: Boundary & Corner Cases (>=5 per feature)

#### Feature R1 Boundary Cases
1. **`test_r1_t2_01_request_missing_x_device_token`**
   - **Endpoint**: `POST /api/sales/push-pc-sale`
   - **Condition**: Omit `X-Device-Token` header.
   - **Expected Status**: `401 Unauthorized` (or `422 Unprocessable Entity`).

2. **`test_r1_t2_02_request_malformed_x_device_token`**
   - **Endpoint**: `POST /api/sales/push-pc-sale`
   - **Condition**: Header `X-Device-Token: INVALID_TOKEN_XYZ_12345`.
   - **Expected Status**: `403 Forbidden` (or `401 Unauthorized`).

3. **`test_r1_t2_03_pair_code_generation_invalid_user`**
   - **Endpoint**: `POST /api/device/pair-token`
   - **Condition**: Body `{"user_id": 999999, "device_name": "Scanner"}`.
   - **Expected Status**: `404 Not Found` (or `400 Bad Request`).

4. **`test_r1_t2_04_revoke_already_revoked_device`**
   - **Endpoint**: `DELETE /api/device/revoke/{device_id}`
   - **Condition**: Issue request on device already marked revoked.
   - **Expected Status**: `400 Bad Request` or `404 Not Found` ("Device token already revoked").

5. **`test_r1_t2_05_repair_device_after_revocation`**
   - **Endpoint**: `POST /api/device/pair-token`
   - **Condition**: Pair device with same `device_name` after revoking previous token.
   - **Expected Status**: `200 OK`
   - **DB Assertion**: Generates new active token; old token record remains revoked/inactive.

---

#### Feature R2 Boundary Cases
1. **`test_r2_t2_01_push_pc_sale_empty_items`**
   - **Endpoint**: `POST /api/sales/push-pc-sale`
   - **Body**: `{"device_token": "<token>", "items": [], "pc_user_id": 1}`
   - **Expected Status**: `400 Bad Request` ("Items list cannot be empty").

2. **`test_r2_t2_02_push_pc_sale_invalid_product_id`**
   - **Endpoint**: `POST /api/sales/push-pc-sale`
   - **Body**: `{"device_token": "<token>", "items": [{"product_id": "NONEXISTENT_PROD", "quantity": 1, "price": 10.0}], "pc_user_id": 1}`
   - **Expected Status**: `400 Bad Request` / `404 Not Found`.

3. **`test_r2_t2_03_phone_checkout_insufficient_stock`**
   - **Endpoint**: `POST /api/sales/phone-checkout`
   - **Body**: `{"device_token": "<token>", "items": [{"product_id": "PROD-001", "quantity": 999999, "price": 10.0}], "payment_type": "cash", "total_amount": 9999990.0, "paid_amount": 9999990.0}`
   - **Expected Status**: `400 Bad Request` ("Mahsulot omborda yetarli emas").

4. **`test_r2_t2_04_phone_checkout_negative_price_or_qty`**
   - **Endpoint**: `POST /api/sales/phone-checkout`
   - **Body**: `{"device_token": "<token>", "items": [{"product_id": "PROD-001", "quantity": -5, "price": -10.0}], "payment_type": "cash", "total_amount": 50.0, "paid_amount": 50.0}`
   - **Expected Status**: `422 Unprocessable Entity` or `400 Bad Request`.

5. **`test_r2_t2_05_phone_checkout_invalid_payment_type`**
   - **Endpoint**: `POST /api/sales/phone-checkout`
   - **Body**: `{"device_token": "<token>", "items": [{"product_id": "PROD-001", "quantity": 1, "price": 10.0}], "payment_type": "crypto_btc", "total_amount": 10.0, "paid_amount": 10.0}`
   - **Expected Status**: `422 Unprocessable Entity` or `400 Bad Request`.

---

#### Feature R3 Boundary Cases
1. **`test_r3_t2_01_respond_nonexistent_push_id`**
   - **Endpoint**: `POST /api/sales/respond-push`
   - **Body**: `{"push_id": "PUSH-99999999", "action": "accept"}`
   - **Expected Status**: `404 Not Found` ("Push notification not found").

2. **`test_r3_t2_02_respond_twice_to_same_push_id`**
   - **Endpoint**: `POST /api/sales/respond-push`
   - **Sequence**: Call `respond-push` with `action="accept"`, then call again with `action="decline"` for same `push_id`.
   - **Expected Status**: 1st call `200 OK`, 2nd call `400 Bad Request` ("Push alert already processed").

3. **`test_r3_t2_03_fetch_payload_for_declined_push`**
   - **Endpoint**: `GET /api/sales/push-payload/{push_id}`
   - **Condition**: Issue request after push has been declined.
   - **Expected Status**: `400 Bad Request` or `404 Not Found` ("Push alert was declined or expired").

4. **`test_r3_t2_04_respond_push_invalid_action`**
   - **Endpoint**: `POST /api/sales/respond-push`
   - **Body**: `{"push_id": "<valid_push_id>", "action": "hold"}`
   - **Expected Status**: `422 Unprocessable Entity` or `400 Bad Request`.

5. **`test_r3_t2_05_pending_pushes_isolation_between_users`**
   - **Endpoint**: `GET /api/sales/pending-pushes`
   - **Condition**: Cashier 1 logs in and requests pending pushes. Scanner pushed alert targeting Cashier 2 (`pc_user_id=2`).
   - **Expected Response**: Array does NOT include Cashier 2's push alert.

---

### Tier 3: Cross-Feature Combinations

1. **`test_t3_01_full_e2e_journey_pair_scan_push_accept_pos_checkout`**
   - **Scenario**: Full end-to-end integration workflow.
   - **Steps**:
     1. User pairs device via `POST /api/device/pair-token` -> obtains `X-Device-Token`.
     2. Mobile scanner scans 3 units of `PROD-001` and 2 units of `PROD-002` in Computer Sale Mode -> calls `POST /api/sales/push-pc-sale` -> gets `push_id`.
     3. PC Cashier checks `GET /api/sales/pending-pushes` -> locates `push_id`.
     4. PC Cashier calls `POST /api/sales/respond-push` (`action="accept"`).
     5. PC POS fetches cart data via `GET /api/sales/push-payload/{push_id}` -> cart populated with 5 total items ($110.0).
     6. PC POS completes sale via `POST /api/sales/checkout`.
   - **Assertions**:
     - `sales_pushes.status == 'accepted'`
     - `sales` table contains final completed sale record.
     - Inventory decremented atomically: `PROD-001` by 3, `PROD-002` by 2.

2. **`test_t3_02_multi_device_pairing_and_selective_revocation`**
   - **Scenario**: Dual mobile devices connected to same user account.
   - **Steps**:
     1. User pairs Device A ("Tablet-1") and Device B ("Phone-2").
     2. Both devices make valid `GET /api/device/list` requests.
     3. User revokes Device A from Personal Center via `DELETE /api/device/revoke/{device_a_id}`.
     4. Device A attempts `POST /api/sales/push-pc-sale` -> receives `403 Forbidden`.
     5. Device B attempts `POST /api/sales/push-pc-sale` -> receives `200 OK` (token remains valid).
   - **Assertions**: Device revocation is targeted and does not impact sibling devices for the same user.

3. **`test_t3_03_mobile_switch_modes_push_then_phone_checkout`**
   - **Scenario**: Mobile scanner switching dynamically between Computer Sale Mode and Phone Sale Mode.
   - **Steps**:
     1. Scanner operates in Computer Sale Mode: pushes Cart 1 to PC -> `push_id_1`.
     2. Scanner switches to Phone Sale Mode: executes `POST /api/sales/phone-checkout` for Cart 2 (Cash).
     3. PC cashier accepts `push_id_1` and completes Cart 1 checkout on PC POS.
   - **Assertions**: Both sales recorded in `sales` DB table independently with accurate payment types (`naqd` for Phone Sale, PC POS payment method for Computer Sale).

4. **`test_t3_04_push_decline_and_resubmit`**
   - **Scenario**: PC cashier declines invalid push; mobile scanner resubmits corrected cart.
   - **Steps**:
     1. Scanner pushes Cart 1 (invalid quantity) -> `push_id_1`.
     2. PC cashier declines via `POST /api/sales/respond-push` (`action="decline"`).
     3. Mobile scanner receives decline status, corrects quantity, and calls `POST /api/sales/push-pc-sale` -> `push_id_2`.
     4. PC cashier accepts `push_id_2` and completes checkout.
   - **Assertions**: `push_id_1` has status `'declined'`, `push_id_2` has status `'accepted'`, single sale record in DB.

---

### Tier 4: Real-World Workloads

1. **`test_t4_01_concurrent_cashiers_push_notifications`**
   - **Scenario**: 5 mobile scanners pushing carts concurrently to 3 distinct PC cashiers.
   - **Execution**: Concurrent async HTTP requests using `httpx.AsyncClient` or Python `concurrent.futures`.
   - **Validation**: Each PC cashier queries `GET /api/sales/pending-pushes` and receives exclusively the push notifications targeted to their `pc_user_id`. No cross-session push leaks or race condition errors.

2. **`test_t4_02_high_volume_phone_checkout_stock_concurrency`**
   - **Scenario**: 10 concurrent mobile phone checkouts against shared stock item (initial stock = 50).
   - **Execution**: 10 simultaneous requests each purchasing 3 units (total 30 units).
   - **Assertions**:
     - All 10 requests succeed (`200 OK`).
     - Exactly 10 sale records created in `sales` table.
     - Final `quantityInStock` in DB equals exactly 20 (50 - 30). No DB lock failures or lost updates.

3. **`test_t4_03_burst_push_notifications_and_queue_handling`**
   - **Scenario**: Rapid burst of 20 mobile push requests sent to a single PC cashier within 1 second.
   - **Assertions**:
     - All 20 requests return `200 OK` with unique `push_id`s.
     - `GET /api/sales/pending-pushes` returns list of 20 pending pushes.
     - Cashier can accept/decline each push in sequence without database corruption or duplicate response errors.

---

## 3. Caveats

1. **Implementation Availability**:
   - As defined in `PROJECT.md`, Milestones 2 and 4 (Backend Device Token & Sales Push endpoints) are in `PLANNED` status. The E2E test suite in `tests/e2e/test_mobile_pos_e2e.py` is written as opaque-box specification against the interface contracts.
   - When Milestones 2 & 4 are implemented by backend agents, all endpoint paths, parameters, headers, and HTTP status codes specified herein MUST be strictly adhered to.
2. **Database Engine & Environment**:
   - The test environment uses SQLite (`erp.db`) or an in-memory SQLite database (`sqlite:///:memory:`) for pytest execution. Concurrency tests (Tier 4) must account for SQLite WAL mode (`PRAGMA journal_mode=WAL;`) or standard transaction handling to avoid `database is locked` operational errors during parallel runs.
3. **Frontend Integration Boundary**:
   - Frontend UI components (`PersonalCenter.vue`, `MobileScanner.vue`, `PosPushAlertModal.vue`) consume these exact REST contract endpoints. Testing at the API level guarantees complete frontend-backend contractual integrity.

---

## 4. Conclusion

This report establishes the complete, requirement-driven opaque-box test specification for Requirements R1, R2, and R3 across Tiers 1 through 4:

- **Total Test Cases Mapped**: 37 detailed test case specifications.
  - **Tier 1 (Feature Coverage)**: 15 tests (5 R1, 5 R2, 5 R3).
  - **Tier 2 (Boundary & Corner Cases)**: 15 tests (5 R1, 5 R2, 5 R3).
  - **Tier 3 (Cross-Feature Combinations)**: 4 multi-device / end-to-end journey tests.
  - **Tier 4 (Real-World Workloads)**: 3 high-concurrency / burst workload tests.

The test design provides 100% coverage of device pairing/revocation, dual mobile sales modes (push vs direct phone POS), and PC alert/cart payload handover contracts.

---

## 5. Verification Method

To independently verify this test specification and run the E2E test suite upon completion of Milestones 2–5:

1. **Test Suite Location**:
   - File: `/home/xasanboy/ERP/tests/e2e/test_mobile_pos_e2e.py`
   - Runner: `/home/xasanboy/ERP/run_e2e_tests.sh`
   - Signal File: `/home/xasanboy/ERP/TEST_READY.md`

2. **Execution Commands**:
   ```bash
   cd /home/xasanboy/ERP
   # Run all E2E pytest cases with verbose output
   pytest tests/e2e/test_mobile_pos_e2e.py -v

   # Alternatively, run via automated test runner script
   bash run_e2e_tests.sh
   ```

3. **Validation Criteria**:
   - All 37 test cases must pass (`PASSED` status).
   - Zero unhandled `500 Internal Server Error` exceptions.
   - DB assertions (stock level decrements, device token status, sales records) pass with exact numerical precision.

4. **Invalidation Conditions**:
   - API response headers missing `X-Device-Token` handling.
   - Status code deviations (e.g. returning `200 OK` on revoked token instead of `403 Forbidden`).
   - SQLite table schema missing `device_tokens` or `sales_pushes` relations.
