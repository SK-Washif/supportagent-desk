from fastapi.testclient import TestClient

from app.main import create_app


def test_health():
    body = TestClient(create_app()).get("/api/health").json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
