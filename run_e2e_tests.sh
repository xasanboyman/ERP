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
