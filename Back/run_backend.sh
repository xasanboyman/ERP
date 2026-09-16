#!/bin/bash
cd "$(dirname "$0")"

# Ensure secure tunnel to PostgreSQL on Oracle VPS 139.185.55.147
if ! ps aux | grep -q "[L] 5433:127.0.0.1:5432"; then
  echo "Establishing secure connection to Database Server (139.185.55.147)..."
  ssh -f -N -o StrictHostKeyChecking=no -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -o ExitOnForwardFailure=yes -L 5433:127.0.0.1:5432 -i /home/xasanboy/Downloads/key.key ubuntu@139.185.55.147 2>/dev/null
fi

echo "Starting Knit ERP Backend on http://0.0.0.0:8000 ..."
exec ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
