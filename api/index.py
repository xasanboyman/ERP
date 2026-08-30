import sys
import os
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
back_dir = os.path.join(parent_dir, "Back")

if back_dir not in sys.path:
    sys.path.insert(0, back_dir)

try:
    from app.main import app as fastapi_app
    app = fastapi_app
except Exception as e:
    tb_str = traceback.format_exc()
    import json

    async def app(scope, receive, send):
        if scope.get("type") == "http":
            response_body = json.dumps({
                "diagnostic_error": "Backend Startup Failed",
                "python_version": sys.version,
                "sys_path": sys.path,
                "traceback": tb_str
            }).encode("utf-8")
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(response_body)).encode("utf-8")),
                ],
            })
            await send({
                "type": "http.response.body",
                "body": response_body,
            })
