#!/bin/bash
set -e

# Navigate to project root
cd /home/xasanboy/ERP

echo "========================================="
echo "Starting Adversarial Test Suite Run..."
echo "========================================="

# 1. Seed database to clear state
echo "1. Seeding database..."
/home/xasanboy/ERP/Back/venv/bin/python Back/seed.py

# 2. Start the backend server in background
echo "2. Starting backend server on port 8000..."
cd Back
/home/xasanboy/ERP/Back/venv/bin/uvicorn app.main:app --port 8000 &
SERVER_PID=$!
cd ..

# Ensure the backend server process is stopped when script finishes or fails
cleanup() {
    echo "========================================="
    echo "Cleaning up..."
    if [ ! -z "$SERVER_PID" ]; then
        echo "Killing backend server (PID $SERVER_PID)..."
        kill -9 $SERVER_PID || true
    fi
    echo "Cleanup complete."
    echo "========================================="
}
trap cleanup EXIT

# 3. Wait for backend to become healthy
echo "3. Waiting for backend server to become healthy..."
/home/xasanboy/ERP/Back/venv/bin/python -c "
import requests, time
for i in range(50):
    try:
        res = requests.get('http://127.0.0.1:8000/')
        if res.status_code == 200:
            print('Backend is healthy!')
            break
    except Exception as e:
        pass
    time.sleep(0.2)
else:
    raise RuntimeError('Backend failed to start in 10s')
"

# 4. Run pytest suite
echo "4. Executing Pytest Adversarial Suite..."
/home/xasanboy/ERP/Back/venv/bin/pytest "$@" -v

echo "========================================="
echo "Adversarial Test Suite Run Complete!"
echo "========================================="
