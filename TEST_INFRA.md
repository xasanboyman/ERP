# E2E Test Suite Infrastructure Documentation

This document describes the design, architecture, feature inventory, coverage tiers, and execution protocol of the requirement-driven E2E test suite for the **Mobile QR/Barcode Scanning System & Dual POS Handover** for ERP.

---

## 1. Architectural Overview & Philosophy

The E2E test suite is constructed as a **requirement-driven, opaque-box API-level verification suite**. It treats the ERP system as a black-box service, interacting exclusively through standard HTTP interfaces, JSON payloads, and authorization headers (`X-Device-Token`).

### Core Design Principles:
1. **Opaque-Box Requirement Traceability**: Every test maps directly to explicit functional requirements (R1: Device Pairing, R2: Dual Sales Modes, R3: PC POS Handover).
2. **Zero-Side-Effect Repeatability**: Each test run starts with a clean database reset via `Back/seed.py`, guaranteeing deterministic behavior across local and CI environments.
3. **Multi-Tiered Coverage Strategy**: Categorized into 4 progressive tiers ranging from basic happy-path feature coverage to real-world concurrent cashier workloads.
4. **Dual Execution Topology**: Supports both live Uvicorn HTTP server execution (default) and fast in-process FastAPI `TestClient` execution via `--in-process`.

---

## 2. Feature Inventory Table

| Req ID | Feature Area | Backend API Endpoints | DB Models / Tables | Target Pytest Module | Key Assertions |
|--------|--------------|-----------------------|---------------------|----------------------|----------------|
| **R1.1** | Pair Code Generation | `POST /api/device/pair-token` | `DeviceToken`, `User` | `test_mobile_pos_e2e.py` | 6-digit pair code, expiration timestamp, active status |
| **R1.2** | Device Token Auth | `X-Device-Token` Header Middleware | `DeviceToken` | `test_mobile_pos_e2e.py` | HTTP 200 for valid token; 401/403 for missing/invalid token |
| **R1.3** | Token Revocation | `DELETE /api/device/revoke/{id}` | `DeviceToken` | `test_mobile_pos_e2e.py` | Token record invalidated; subsequent request yields HTTP 403 |
| **R2.1** | Computer Sale Push | `POST /api/sales/push-pc-sale` | `SalesPush`, `Product` | `test_mobile_pos_e2e.py` | Push ID generated; status set to `pending`; item array validated |
| **R2.2** | Mobile Cash POS | `POST /api/sales/phone-checkout` | `Sale`, `SaleItem` | `test_mobile_pos_e2e.py` | Payment type `cash`; total amount matched; stock quantity decremented |
| **R2.3** | Mobile Card POS | `POST /api/sales/phone-checkout` | `Sale`, `SaleItem` | `test_mobile_pos_e2e.py` | Payment type `card`; transaction recorded |
| **R2.4** | Mobile Debt POS | `POST /api/sales/phone-checkout` | `Sale`, `SaleItem` | `test_mobile_pos_e2e.py` | Payment type `debt`; debt balance recorded |
| **R3.1** | PC Alert & Payload | `GET /api/sales/pending-pushes`<br>`GET /api/sales/push-payload/{id}` | `SalesPush` | `test_mobile_pos_e2e.py` | Active push listed for PC session; payload pre-fills POS cart |
| **R3.2** | Accept/Decline Handover | `POST /api/sales/respond-push` | `SalesPush` | `test_mobile_pos_e2e.py` | Accept transitions push to `accepted` & opens cart; Decline sets `declined` |

---

## 3. System Architecture & Execution Flow

```
+-----------------------------------------------------------------------------------+
|                                  run_e2e_tests.sh                                 |
+-----------------------------------------------------------------------------------+
       |                                      |                               |
       v (1. Reset Schema)                    v (2. Spawn Daemon)             v (3. Run Pytest)
+-----------------------+              +-----------------------+    +-----------------------+
|  Back/seed.py         |              | Uvicorn Server        |    | Pytest Suite          |
|  (SQLite DB Reset)    |              | (127.0.0.1:8000)      |    | test_mobile_pos_e2e.py|
+-----------------------+              +-----------------------+    +-----------------------+
                                                  ^                             |
                                                  | (HTTP REST + X-Device-Token)|
                                                  +-----------------------------+
```

---

## 4. Coverage Tiers & Minimum Thresholds

The test suite enforces a total threshold of **>= 95 test cases** across 4 tiers:

### Tier 1: Feature Coverage (45 Tests)
- **R1 Pairing & Auth (15 tests)**: Pair code creation, token verification, device listing, revocation, multi-device pairing.
- **R2 Sales Modes (20 tests)**: Computer Sale push payloads, Cash/Card/Debt mobile POS checkouts, stock decrements, discounts, customer info.
- **R3 PC POS Handover (10 tests)**: Pending push polling, accept response, decline response, cart pre-fill payload, checkout after handover.

### Tier 2: Boundary & Corner Cases (40 Tests)
- **R1 Boundary (15 tests)**: Unauthenticated requests, revoked token reuse, re-pairing post revocation, invalid user IDs.
- **R2 Boundary (15 tests)**: Empty cart push, negative item price/quantity, invalid payment types, insufficient stock checks.
- **R3 Boundary (10 tests)**: Nonexistent push ID response (404), duplicate response to same push ID (400), declined push payload fetch rejection, user isolation.

### Tier 3: Cross-Feature Combinations (5 Tests)
- End-to-end user journeys combining Device Pairing -> Item Scan -> PC Push -> PC Accept -> Cart Population -> Checkout.
- Multi-device pairing per user account with selective device token revocation.
- Switching mobile scanner modes dynamically between Computer Push and Standalone Checkout.
- Decline push and resubmit modified cart.

### Tier 4: Real-World Application Workloads (5 Tests)
- Multi-cashier push handover isolation.
- High-volume parallel phone checkouts under stock concurrency.
- Rapid burst push notifications queue handling.
- Mixed workload pushes and direct checkouts.
- Multi-user token lifecycle management under load.

---

## 5. Execution Protocols & CLI Instructions

### Primary Execution (In-Process Fast Mode):
```bash
cd /home/xasanboy/ERP
./run_e2e_tests.sh --in-process
```

### Live Daemon Server Mode:
```bash
cd /home/xasanboy/ERP
./run_e2e_tests.sh --port 8000
```

### Pytest Direct Execution:
```bash
cd /home/xasanboy/ERP
PYTHONPATH=Back ./Back/venv/bin/pytest tests/e2e/test_mobile_pos_e2e.py -v
```

---

## 6. Troubleshooting & Maintenance

- **Port 8000 in use**: Run `./run_e2e_tests.sh --port 8005` or kill existing process with `fuser -k 8000/tcp`.
- **Module import error (`No module named 'app'`)**: Ensure `PYTHONPATH=Back` is exported or included in the command line.
- **Database Lock**: Ensure no external SQLite browser has `erp.db` open during `seed.py` reset.
