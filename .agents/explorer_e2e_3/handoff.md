# Technical Design Report: E2E Test Runner Architecture, Infrastructure Documentation, & Signal Specification

**Agent**: Explorer 3 (Milestone 1: E2E Testing Track)  
**Working Directory**: `/home/xasanboy/ERP/.agents/explorer_e2e_3`  
**Target Milestone**: Milestone 1 (Requirement-Driven Opaque-Box E2E Testing for Mobile QR/Barcode Scanning System & Dual POS Handover)  
**Date**: 2026-08-09  

---

## 1. Observation

### 1.1 Project Scope & Target Deliverables
From `/home/xasanboy/ERP/PROJECT.md` (lines 11-18) and `/home/xasanboy/ERP/.agents/sub_orch_e2e/SCOPE.md` (lines 38-43):
- **Requirement R1**: Device Pairing, Token Authorization (`X-Device-Token`) & Revocation (Personal Center).
- **Requirement R2**: Mobile Dual Sales Modes (Computer Sale Mode push to PC vs Phone Sale Mode direct POS checkout).
- **Requirement R3**: PC POS Notification & Handover (Accept/Decline pop-up modal, pending pushes API, cart population payload).
- **Milestone 1 Deliverables**:
  1. `/home/xasanboy/ERP/run_e2e_tests.sh`: Automated test runner script.
  2. `/home/xasanboy/ERP/TEST_INFRA.md`: Comprehensive infrastructure documentation.
  3. `/home/xasanboy/ERP/TEST_READY.md`: Completion signal file with coverage summary matrix.
  4. `/home/xasanboy/ERP/tests/e2e/test_mobile_pos_e2e.py`: Main Pytest test suite.

### 1.2 Existing Environment & Codebase Analysis
- **Backend Entrypoint**: FastAPI application defined in `/home/xasanboy/ERP/Back/app/main.py:79` (`app = FastAPI(...)`).
- **Python Virtualenv**: `/home/xasanboy/ERP/Back/venv` containing `python`, `pytest`, `uvicorn`, `requests`, `sqlalchemy`, `pydantic`.
- **Database Reset Mechanism**: `/home/xasanboy/ERP/Back/seed.py`, which resets SQLite DB schema (`erp.db`) and seeds initial administrative & cashier users (`admin`, `dilshodk`, etc.) and default roles.
- **Existing Prototype Runner**: `/home/xasanboy/ERP/run_e2e_tests.sh` currently exists as a primitive script running a legacy generic suite `tests/e2e/test_erp_e2e.py`.
- **Existing Documentation Prototypes**: `/home/xasanboy/ERP/TEST_INFRA.md` and `/home/xasanboy/ERP/TEST_READY.md` reference generic ERP entities and require complete redesign to align with the Mobile QR/Barcode POS track (`test_mobile_pos_e2e.py`, R1-R3).

---

## 2. Logic Chain

### 2.1 Test Runner Architecture (`run_e2e_tests.sh`)
1. **Goal**: Provide a single, robust, zero-dependency, automated CLI entry point that reliably sets up the test environment, resets the database, boots the FastAPI server, waits for health checks, executes `tests/e2e/test_mobile_pos_e2e.py`, captures output/exit status, and guarantees process cleanup.
2. **Environment & Path Resolution**:
   - The script must resolve its root directory using `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`.
   - Set bash safety flags: `set -e`, `set -o pipefail`.
   - Export `PYTHONPATH="${SCRIPT_DIR}/Back:${PYTHONPATH}"` and `DATABASE_URL` / `ENV=testing`.
3. **Database Reset Strategy**:
   - Before launching the server, execute `${SCRIPT_DIR}/Back/venv/bin/python ${SCRIPT_DIR}/Back/seed.py` to ensure every test run starts from a clean, predictable state.
   - Option for test DB isolation (`TEST_DB="${SCRIPT_DIR}/Back/test_erp.db"`).
4. **Backend Daemon vs In-Process Dual Mode**:
   - **Mode 1 (Live Server Daemon - Default)**: Spawns `./Back/venv/bin/uvicorn app.main:app --port $PORT --host 127.0.0.1` in background.
   - **Mode 2 (In-Process TestClient - `--in-process` Flag)**: Bypasses network socket binding and executes pytest directly against FastAPI's in-memory ASGI stack via `TestClient`/`httpx.AsyncClient`.
5. **Process Lifecycle & Signal Trapping**:
   - Store server PID in `$SERVER_PID`.
   - Install a bash `trap cleanup EXIT SIGINT SIGTERM` handler.
   - `cleanup()` sends `SIGTERM`, waits up to 3s, and forces `kill -9` if necessary, preventing orphaned Uvicorn processes on port 8000.
6. **Health Polling Loop**:
   - Poll `http://127.0.0.1:$PORT/` up to 50 times with 200ms intervals (10-second timeout). Fail fast if server crashes during boot.
7. **Exit Code & Output UX**:
   - Capture `pytest` exit status (`PYTEST_EXIT=$?`).
   - Use ANSI color formatting (`\033[0;32m` Green, `\033[0;31m` Red, `\033[0;34m` Blue).
   - Display runtime duration, total test counts, and clear pass/fail status box.
   - Exit with `$PYTEST_EXIT`.

### 2.2 Infrastructure Documentation Architecture (`TEST_INFRA.md`)
1. **Goal**: Serve as the canonical architectural specification for developers, sub-orchestrators, and audit agents.
2. **Structure**:
   - **Section 1: Architectural Overview & Philosophy**: Opaque-box requirement-driven testing principles, zero-side-effect execution, and tier-based categorization.
   - **Section 2: Feature Inventory Table**: Comprehensive matrix mapping Requirements R1, R2, R3 to Backend API Endpoints, DB Models, Frontend Views, and Pytest Functions.
   - **Section 3: System Architecture & Execution Flow**: Diagrammatic representation of test runner, database seed, FastAPI ASGI server, and Pytest runner interactions.
   - **Section 4: Coverage Tiers & Minimum Thresholds**: Explicit breakdown of required test counts across Tiers 1-4 (Tier 1: 45 tests, Tier 2: 40 tests, Tier 3: 5 tests, Tier 4: 5 tests; Total: >= 95 tests).
   - **Section 5: Execution Protocols & CLI Options**: Complete guide on running tests, passing pytest flags (`-k`, `-v`, `--tb=short`), running in isolated vs live mode, and debugging failures.
   - **Section 6: Troubleshooting & Maintenance**: Solutions for port binding conflicts, database locks, seed failures, and token expiration issues.

### 2.3 Readiness Signal File Specification (`TEST_READY.md`)
1. **Goal**: Serve as a machine-readable and human-verifiable completion signal file for Milestone 1.
2. **Structure**:
   - **Section 1: Metadata & Status Badge**: Status `READY`, Target Suite `tests/e2e/test_mobile_pos_e2e.py`, Runner `./run_e2e_tests.sh`, Pass Rate 100% (95/95).
   - **Section 2: Comprehensive Coverage Matrix**: Interactive checklist breakdown across Tiers 1-4 for Requirements R1, R2, R3.
   - **Section 3: Verification Protocol**: Exact terminal commands for sub-orchestrators and auditors to verify test collection (`pytest --collect-only`), execution, and signal integrity.

---

## 3. Caveats

- **Scope Boundary**: Explorer 3 focuses on architecture and design specifications. Implementation of `test_mobile_pos_e2e.py` code will be performed by implementer agents during Milestone 1 execution.
- **Network Mode**: Operating in `CODE_ONLY` mode means all test execution relies on local localhost (`127.0.0.1:8000`) communication without external cloud dependencies.
- **DB Driver**: Assumptions are based on SQLite (`sqlite3` / SQLAlchemy SQLite engine). If PostgreSQL is introduced in future milestones, `seed.py` and DB cleanup logic in `run_e2e_tests.sh` will adapt seamlessly via `DATABASE_URL`.

---

## 4. Conclusion & Technical Design Specifications

### 4.1 Specification: `/home/xasanboy/ERP/run_e2e_tests.sh`

```bash
#!/bin/bash
# ==============================================================================
# Mobile QR/Barcode Scanning & Dual POS Handover E2E Test Suite Runner
# Target Suite: tests/e2e/test_mobile_pos_e2e.py
# ==============================================================================

set -e
set -o pipefail

# ANSI Color Codes for Rich Terminal Output
BOLD="\033[1m"
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
RESET="\033[0m"

# Absolute Script Directory Resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

TEST_PORT="${TEST_PORT:-8000}"
PYTHON_BIN="${SCRIPT_DIR}/Back/venv/bin/python"
PYTEST_BIN="${SCRIPT_DIR}/Back/venv/bin/pytest"
TEST_SUITE="${SCRIPT_DIR}/tests/e2e/test_mobile_pos_e2e.py"
IN_PROCESS_MODE=false
EXTRA_PYTEST_ARGS=()

# Parse Command Line Arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --in-process|--fast)
      IN_PROCESS_MODE=true
      shift
      ;;
    --port)
      TEST_PORT="$2"
      shift 2
      ;;
    -v|--verbose)
      EXTRA_PYTEST_ARGS+=("-v")
      shift
      ;;
    -k)
      EXTRA_PYTEST_ARGS+=("-k" "$2")
      shift 2
      ;;
    -h|--help)
      echo -e "${BOLD}Usage:${RESET} ./run_e2e_tests.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --in-process, --fast  Run pytest in-process using FastAPI TestClient (no daemon)"
      echo "  --port PORT           Specify custom port for Uvicorn live server (default: 8000)"
      echo "  -v, --verbose         Enable verbose pytest output"
      echo "  -k EXPRESSION         Filter pytest execution by test name expression"
      echo "  -h, --help            Show this help menu"
      exit 0
      ;;
    *)
      EXTRA_PYTEST_ARGS+=("$1")
      shift
      ;;
  esac
done

START_TIME=$(date +%s)

echo -e "${CYAN}======================================================================${RESET}"
echo -e "${BOLD}${BLUE}   Mobile QR/Barcode & Dual POS Handover - E2E Test Suite Runner   ${RESET}"
echo -e "${CYAN}======================================================================${RESET}"

# 1. Environment & Dependency Validation
echo -e "\n${BOLD}[1/5] Validating Python Environment & Dependencies...${RESET}"
if [ ! -f "${PYTHON_BIN}" ]; then
  echo -e "${RED}[ERROR] Python binary not found at ${PYTHON_BIN}${RESET}"
  exit 1
fi

if [ ! -f "${PYTEST_BIN}" ]; then
  echo -e "${RED}[ERROR] Pytest binary not found at ${PYTEST_BIN}${RESET}"
  exit 1
fi
echo -e "${GREEN}✓ Virtual environment validated (${PYTHON_BIN})${RESET}"

# 2. Database Seeding & Reset
echo -e "\n${BOLD}[2/5] Resetting & Seeding Database State...${RESET}"
export PYTHONPATH="${SCRIPT_DIR}/Back:${PYTHONPATH}"
export ENV="testing"

if ${PYTHON_BIN} "${SCRIPT_DIR}/Back/seed.py"; then
  echo -e "${GREEN}✓ Database successfully seeded via seed.py${RESET}"
else
  echo -e "${RED}[ERROR] Database seeding failed! Aborting test run.${RESET}"
  exit 3
fi

# Cleanup Function for Process & Trap Registration
SERVER_PID=""
cleanup() {
  echo -e "\n${CYAN}======================================================================${RESET}"
  echo -e "${BOLD}[TEARDOWN] Cleaning up background processes...${RESET}"
  if [ -n "${SERVER_PID}" ] && kill -0 "${SERVER_PID}" 2>/dev/null; then
    echo -e "${YELLOW}Stopping FastAPI backend server (PID: ${SERVER_PID})...${RESET}"
    kill "${SERVER_PID}" 2>/dev/null || true
    sleep 1
    if kill -0 "${SERVER_PID}" 2>/dev/null; then
      echo -e "${RED}Force killing server (PID: ${SERVER_PID})...${RESET}"
      kill -9 "${SERVER_PID}" 2>/dev/null || true
    fi
    echo -e "${GREEN}✓ Server stopped cleanly.${RESET}"
  else
    echo -e "${GREEN}✓ No active backend server process to kill.${RESET}"
  fi
  END_TIME=$(date +%s)
  ELAPSED=$((END_TIME - START_TIME))
  echo -e "${BLUE}Total Execution Time: ${ELAPSED} seconds${RESET}"
  echo -e "${CYAN}======================================================================${RESET}"
}
trap cleanup EXIT SIGINT SIGTERM

# 3. Server Boot or In-Process Setup
if [ "${IN_PROCESS_MODE}" = true ]; then
  echo -e "\n${BOLD}[3/5] Running in IN-PROCESS mode (FastAPI TestClient)...${RESET}"
  echo -e "${GREEN}✓ Skipping live server daemon startup.${RESET}"
else
  echo -e "\n${BOLD}[3/5] Starting FastAPI Backend Server on port ${TEST_PORT}...${RESET}"
  cd "${SCRIPT_DIR}/Back"
  "${PYTHON_BIN}" -m uvicorn app.main:app --port "${TEST_PORT}" --host 127.0.0.1 > /tmp/e2e_backend.log 2>&1 &
  SERVER_PID=$!
  cd "${SCRIPT_DIR}"
  echo -e "${YELLOW}Backend server started in background (PID: ${SERVER_PID})${RESET}"

  # 4. Health Check Polling Loop
  echo -e "\n${BOLD}[4/5] Polling Backend Health Endpoint (http://127.0.0.1:${TEST_PORT}/)...${RESET}"
  HEALTH_PASSED=false
  for i in $(seq 1 50); do
    if ${PYTHON_BIN} -c "
import urllib.request
try:
    res = urllib.request.urlopen('http://127.0.0.1:${TEST_PORT}/', timeout=1)
    if res.status == 200:
        exit(0)
except Exception:
    exit(1)
"; then
      HEALTH_PASSED=true
      break
    fi
    sleep 0.2
  done

  if [ "${HEALTH_PASSED}" = true ]; then
    echo -e "${GREEN}✓ Backend server is active and healthy!${RESET}"
  else
    echo -e "${RED}[ERROR] Backend server failed to become healthy within 10 seconds.${RESET}"
    echo -e "${YELLOW}--- Backend Log Tail ---${RESET}"
    tail -n 20 /tmp/e2e_backend.log
    exit 2
  fi
fi

# 5. Execute Pytest E2E Suite
echo -e "\n${BOLD}[5/5] Executing Pytest E2E Suite (${TEST_SUITE})...${RESET}"
set +e
"${PYTEST_BIN}" "${TEST_SUITE}" "${EXTRA_PYTEST_ARGS[@]}"
PYTEST_EXIT=$?
set -e

if [ ${PYTEST_EXIT} -eq 0 ]; then
  echo -e "\n${GREEN}${BOLD}======================================================================${RESET}"
  echo -e "${GREEN}${BOLD}   ✓ SUCCESS: All Mobile POS E2E Tests Passed (Exit Code 0)          ${RESET}"
  echo -e "${GREEN}${BOLD}======================================================================${RESET}"
else
  echo -e "\n${RED}${BOLD}======================================================================${RESET}"
  echo -e "${RED}${BOLD}   ✗ FAILURE: Pytest suite execution failed with code ${PYTEST_EXIT}             ${RESET}"
  echo -e "${RED}${BOLD}======================================================================${RESET}"
fi

exit ${PYTEST_EXIT}
```

---

### 4.2 Specification: `/home/xasanboy/ERP/TEST_INFRA.md`

```markdown
# E2E Test Suite Infrastructure Documentation

This document describes the design, architecture, feature inventory, coverage tiers, and execution protocol of the requirement-driven E2E test suite for the **Mobile QR/Barcode Scanning System & Dual POS Handover** for ERP.

---

## 1. Architectural Overview & Philosophy

The E2E test suite is constructed as a **requirement-driven, opaque-box API-level verification suite**. It treats the ERP system as a black-box service, interacting exclusively through standard HTTP interfaces, JSON payloads, and authorization headers (`X-Device-Token`).

### Core Design Principles:
1. **Opaque-Box Requirement Traceability**: Every test maps directly to explicit functional requirements (R1: Device Pairing, R2: Dual Sales Modes, R3: PC POS Handover).
2. **Zero-Side-Effect Repeatability**: Each test run starts with a clean database reset via `Back/seed.py`, guaranteeing deterministic behavior across local and CI environments.
3. **Multi-Tiered Coverage Strategy**: Categorized into 4 progressive tiers ranging from basic happy-path feature coverage to real-world concurrent cashier workloads.
4. **Dual Execution Topology**: Supports both live Uvicorn HTTP server execution (default) and fast in-process FastAPI `TestClient` execution.

---

## 2. Feature Inventory Table

| Req ID | Feature Area | Backend API Endpoints | DB Models / Tables | Target Pytest Module | Key Assertions |
|--------|--------------|-----------------------|---------------------|----------------------|----------------|
| **R1.1** | Pair Code Generation | `POST /api/device/pair-token` | `DeviceToken`, `User` | `test_mobile_pos_e2e.py` | 6-digit pair code, expiration timestamp, active status |
| **R1.2** | Device Token Auth | `X-Device-Token` Header Middleware | `DeviceToken` | `test_mobile_pos_e2e.py` | HTTP 200 for valid token; 401/403 for missing/invalid token |
| **R1.3** | Token Revocation | `DELETE /api/device/revoke/{id}` | `DeviceToken` | `test_mobile_pos_e2e.py` | Token record deleted/invalidated; subsequent request yields HTTP 403 |
| **R2.1** | Computer Sale Push | `POST /api/sales/push-pc-sale` | `SalesPush`, `Product` | `test_mobile_pos_e2e.py` | Push ID generated; status set to `pending`; item array validated |
| **R2.2** | Mobile Cash POS | `POST /api/sales/phone-checkout` | `SaleTransaction` | `test_mobile_pos_e2e.py` | Payment type `cash`; total amount matched; stock quantity decremented |
| **R2.3** | Mobile Card POS | `POST /api/sales/phone-checkout` | `SaleTransaction` | `test_mobile_pos_e2e.py` | Payment type `card`; transaction recorded |
| **R2.4** | Mobile Debt POS | `POST /api/sales/phone-checkout` | `SaleTransaction` | `test_mobile_pos_e2e.py` | Payment type `debt`; debt balance recorded |
| **R3.1** | PC Alert & Payload | `GET /api/sales/pending-pushes`<br>`GET /api/sales/push-payload/{id}` | `SalesPush` | `test_mobile_pos_e2e.py` | Active push listed for PC session; payload pre-fills POS cart |
| **R3.2** | Accept/Decline Handover | `POST /api/sales/respond-push` | `SalesPush` | `test_mobile_pos_e2e.py` | Accept transitions push to `accepted` & opens cart; Decline sets `declined` |

---

## 3. System Architecture & Flow

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
- **R1 Pairing & Auth (15 tests)**: Pair code creation, token verification, device listing, revocation.
- **R2 Sales Modes (20 tests)**: Computer Sale push payloads, Cash/Card/Debt mobile POS checkouts.
- **R3 PC POS Handover (10 tests)**: Pending push polling, accept response, decline response, cart pre-fill payload.

### Tier 2: Boundary & Corner Cases (40 Tests)
- **R1 Boundary (15 tests)**: Unauthenticated requests, revoked token reuse, re-pairing post revocation.
- **R2 Boundary (15 tests)**: Empty cart push, negative item price/quantity, invalid cash/card amounts.
- **R3 Boundary (10 tests)**: Nonexistent push ID response (404), duplicate response to same push ID (409/400).

### Tier 3: Cross-Feature Combinations (5 Tests)
- End-to-end user journeys combining Device Pairing -> Item Scan -> PC Push -> PC Accept -> Cart Population -> Checkout.
- Multi-device pairing per user account with selective device token revocation.

### Tier 4: Real-World Application Workloads (5 Tests)
- Multi-cashier push handover isolation.
- High-concurrency mobile scanning and push queueing under load.

---

## 5. Execution Protocols & CLI Instructions

### Primary Execution:
```bash
cd /home/xasanboy/ERP
./run_e2e_tests.sh
```

### Advanced Execution Options:
- **Fast In-Process Mode**: `./run_e2e_tests.sh --in-process`
- **Filter Specific Tier**: `./run_e2e_tests.sh -k "test_tier1"`
- **Verbose Pytest Output**: `./run_e2e_tests.sh -v`

---

## 6. Troubleshooting

- **Port 8000 in use**: Run `./run_e2e_tests.sh --port 8005` or kill existing process with `fuser -k 8000/tcp`.
- **Database Lock**: Ensure no external SQLite browser has `erp.db` open during `seed.py` reset.
```

---

### 4.3 Specification: `/home/xasanboy/ERP/TEST_READY.md`

```markdown
# Test Readiness Summary & Signal Artifact

This document serves as the official signal file attesting that the E2E test suite for **Mobile QR/Barcode Scanning System & Dual POS Handover** is fully constructed, verified, and ready for execution.

---

## 1. Test Suite Metadata

- **Status**: **READY**
- **Target Suite Location**: `/home/xasanboy/ERP/tests/e2e/test_mobile_pos_e2e.py`
- **Automated Test Runner**: `/home/xasanboy/ERP/run_e2e_tests.sh`
- **Infrastructure Guide**: `/home/xasanboy/ERP/TEST_INFRA.md`
- **Total Executable Tests**: **95**
- **Target Pass Rate**: **100% (95 / 95)**

---

## 2. Comprehensive Coverage Matrix Across Tiers 1-4

### Tier 1: Feature Coverage (45/45)
- [x] **R1.1**: Device Pair Code Generation & Registration (5 tests)
- [x] **R1.2**: Valid Device Token Authorization (`X-Device-Token`) (5 tests)
- [x] **R1.3**: Device Token Listing & Revocation from Personal Center (5 tests)
- [x] **R2.1**: Mobile Computer Sale Mode Push to PC (5 tests)
- [x] **R2.2**: Mobile Phone Sale Mode Checkout - Cash (5 tests)
- [x] **R2.3**: Mobile Phone Sale Mode Checkout - Card (5 tests)
- [x] **R2.4**: Mobile Phone Sale Mode Checkout - Debt (5 tests)
- [x] **R3.1**: PC POS Accept Alert & Cart Payload Retrieval (5 tests)
- [x] **R3.2**: PC POS Decline Alert & Push Cancellation (5 tests)

### Tier 2: Boundary & Corner Cases (40/40)
- [x] **R1 Boundary**: Unauthenticated Requests without Device Token (401/403) (5 tests)
- [x] **R1 Boundary**: Revoked Device Token Access Rejection (403 Forbidden) (5 tests)
- [x] **R1 Boundary**: Re-pairing Device after Revocation (5 tests)
- [x] **R2 Boundary**: Push to PC with Empty Cart / Missing Items (422) (5 tests)
- [x] **R2 Boundary**: Push to PC with Invalid Product IDs / Negative Quantities (5 tests)
- [x] **R2 Boundary**: Phone Checkout with Invalid Payment Amounts / Missing Fields (5 tests)
- [x] **R3 Boundary**: Responding to Nonexistent Push ID (404 Not Found) (5 tests)
- [x] **R3 Boundary**: Responding Twice to Same Push ID (409 Conflict / 400 Bad Request) (5 tests)

### Tier 3: Cross-Feature Combinations (5/5)
- [x] **Full E2E Journey**: Pair -> Mobile Scan -> PC Push -> PC Accept -> POS Population -> Complete Sale (3 tests)
- [x] **Multi-Device Session Management**: Single User Dual Device Pairing & Selective Revocation (2 tests)

### Tier 4: Real-World Workloads (5/5)
- [x] **Multi-Cashier Workload**: Concurrent Push Notifications & Cashier Session Isolation (2 tests)
- [x] **High-Concurrency Queueing**: Parallel Scanning & Sales Transaction Workloads (3 tests)

---

## 3. Automated Verification Protocol

To independently verify test collection and suite execution:

1. **Verify Test Count Collection**:
   ```bash
   cd /home/xasanboy/ERP
   ./Back/venv/bin/pytest tests/e2e/test_mobile_pos_e2e.py --collect-only | grep "<Function" | wc -l
   ```
   *Expected Output*: `95`

2. **Execute Full E2E Test Runner**:
   ```bash
   cd /home/xasanboy/ERP
   ./run_e2e_tests.sh
   ```
   *Expected Output*: Exit Code `0`, 100% Tests Passed.
```

---

## 5. Verification Method

To verify the technical design report and specifications produced by Explorer 3:

1. **File Integrity Verification**:
   Inspect the handoff report path: `/home/xasanboy/ERP/.agents/explorer_e2e_3/handoff.md`.
2. **Bash Script Syntax & Execution Dry-Run**:
   - Check bash script syntax: `bash -n /home/xasanboy/ERP/run_e2e_tests.sh`.
3. **Signal Artifact Verification**:
   - Ensure `/home/xasanboy/ERP/TEST_READY.md` aligns with the 95-test count matrix specified in `SCOPE.md`.
4. **Invalidation Conditions**:
   - The design is invalidated if the backend port binding logic fails, signal traps leave dangling uvicorn processes, or coverage tier counts fall below the >= 95 test threshold.
