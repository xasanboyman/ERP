import os
import sys

# Add Back directory to Python module search path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
back_dir = os.path.join(parent_dir, "Back")

if back_dir not in sys.path:
    sys.path.insert(0, back_dir)

from app.main import app as fastapi_app

# Vercel ASGI Application Handler
# Handles both /api/xxx and /xxx routes smoothly
async def app(scope, receive, send):
    if scope.get("type") in ("http", "websocket"):
        path = scope.get("path", "")
        if path.startswith("/api/"):
            scope = dict(scope)
            scope["path"] = path[4:]  # map /api/user/login -> /user/login
        elif path == "/api":
            scope = dict(scope)
            scope["path"] = "/"
    await fastapi_app(scope, receive, send)
