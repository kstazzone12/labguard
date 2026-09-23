from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_declares_synthetic_mode() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "synthetic-data-only"}
