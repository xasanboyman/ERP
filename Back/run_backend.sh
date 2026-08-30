#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Knit ERP Backend on http://0.0.0.0:8000 ..."
exec ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
