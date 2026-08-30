#!/usr/bin/env bash
# ERP AI MCP Server Runner Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${SCRIPT_DIR}/Back/venv/bin/python3"
MCP_SERVER="${SCRIPT_DIR}/Back/mcp_server.py"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Virtualenv python not found at $VENV_PYTHON"
    exit 1
fi

exec "$VENV_PYTHON" "$MCP_SERVER" "$@"
