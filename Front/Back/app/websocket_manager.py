import asyncio
import json
import logging
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("erp.websocket")

class ConnectionManager:
    """
    Central WebSocket Connection Manager for ERP real-time reactive sync.
    Maintains active connections and broadcasts entity change notifications
    (sales, products, inventory, cutting, devices, HR) to clients.
    """
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.user_connections: Dict[int, Set[WebSocket]] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    async def connect(self, websocket: WebSocket, user_id: Optional[int] = None):
        await websocket.accept()
        self.active_connections.add(websocket)
        if user_id is not None:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
        logger.info(f"WebSocket client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: Optional[int] = None):
        self.active_connections.discard(websocket)
        if user_id is not None and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        logger.info(f"WebSocket client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcasts a JSON-serializable message to all connected clients."""
        if not self.active_connections:
            return

        payload_str = json.dumps(message)
        dead_connections = []

        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload_str)
            except Exception as e:
                logger.debug(f"Failed to send to websocket: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.active_connections.discard(dead)

    async def send_to_user(self, user_id: int, message: Dict[str, Any]):
        """Sends a message to a specific user's active connections."""
        connections = self.user_connections.get(user_id, set())
        if not connections:
            return

        payload_str = json.dumps(message)
        dead_connections = []

        for connection in list(connections):
            try:
                await connection.send_text(payload_str)
            except Exception as e:
                logger.debug(f"Failed to send to user {user_id} websocket: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            connections.discard(dead)
            self.active_connections.discard(dead)

    def broadcast_sync(
        self,
        entity: str,
        action: str,
        entity_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        actor: str = "system",
        target_user_id: Optional[int] = None
    ):
        """
        Thread-safe sync helper to broadcast events from synchronous FastAPI endpoints / SQLAlchemy hooks.
        """
        import datetime
        message = {
            "type": "entity_changed",
            "event": "entity_changed",
            "entity": entity,
            "action": action,
            "id": str(entity_id) if entity_id is not None else None,
            "data": data,
            "actor": actor,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }

        try:
            loop = self._loop
            if loop is None:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

            if loop is not None and loop.is_running():
                if target_user_id is not None:
                    asyncio.run_coroutine_threadsafe(self.send_to_user(target_user_id, message), loop)
                else:
                    asyncio.run_coroutine_threadsafe(self.broadcast(message), loop)
            else:
                new_loop = asyncio.new_event_loop()
                if target_user_id is not None:
                    new_loop.run_until_complete(self.send_to_user(target_user_id, message))
                else:
                    new_loop.run_until_complete(self.broadcast(message))
                new_loop.close()
        except Exception as e:
            logger.debug(f"Could not broadcast sync event: {e}")


# Global connection manager singleton
manager = ConnectionManager()
