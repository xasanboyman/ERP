import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket_manager import manager
from app import auth

logger = logging.getLogger("erp.ws_router")
router = APIRouter(tags=["Real-Time WebSockets"])

@router.websocket("/ws/events")
@router.websocket("/api/ws/events")
async def websocket_events_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    user_id = None
    if token:
        try:
            payload = auth.decode_access_token(f"Bearer {token}")
            if isinstance(payload, dict) and "sub" in payload:
                # payload['sub'] is user identifier / username
                user_id = payload.get("id")
        except Exception as e:
            logger.debug(f"WS auth token decode note: {e}")

    await manager.connect(websocket, user_id=user_id)
    
    # Send immediate connection acknowledgment
    await websocket.send_text(json.dumps({
        "type": "connection_ack",
        "status": "connected",
        "message": "Real-time reactive sync active"
    }))

    try:
        while True:
            # Handle incoming client messages (heartbeat pings, subscriptions)
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get("type", "")
                if msg_type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong", "timestamp": msg.get("timestamp")}))
                elif msg_type == "subscribe":
                    # Client can subscribe to specific entity channels if desired
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "channels": msg.get("channels", ["all"])
                    }))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id=user_id)
    except Exception as e:
        logger.debug(f"WS error: {e}")
        manager.disconnect(websocket, user_id=user_id)
