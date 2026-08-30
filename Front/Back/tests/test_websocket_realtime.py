import pytest
import json
from fastapi.testclient import TestClient
from app.main import app
from app.websocket_manager import manager

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_websocket_connection_and_ping(client):
    with client.websocket_connect("/ws/events") as websocket:
        data = websocket.receive_text()
        ack = json.loads(data)
        assert ack.get("type") == "connection_ack"
        assert ack.get("status") == "connected"

        # Test heartbeat ping
        websocket.send_text(json.dumps({"type": "ping", "timestamp": 123456789}))
        response = websocket.receive_text()
        pong = json.loads(response)
        assert pong.get("type") == "pong"
        assert pong.get("timestamp") == 123456789

def test_websocket_broadcast_on_activity_log(client):
    with client.websocket_connect("/ws/events") as websocket:
        # Drain initial ack
        _ = websocket.receive_text()

        # Manually trigger a broadcast or call endpoint
        manager.broadcast_sync(
            entity="products",
            action="updated",
            entity_id="PROD-TEST-123",
            data={"productName": "Test Shirt", "price": 45.0}
        )

        msg_str = websocket.receive_text()
        msg = json.loads(msg_str)
        assert msg.get("entity") == "products"
        assert msg.get("action") == "updated"
        assert msg.get("id") == "PROD-TEST-123"
        assert msg.get("data", {}).get("productName") == "Test Shirt"
