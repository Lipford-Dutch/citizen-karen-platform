import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app import main


class DummyPlugin:
    async def submit(self, complaint):
        return {"state": "submitted", "agency_reference": "REF-123"}


def setup_function():
    main.complaints_store.clear()


def test_health():
    client = TestClient(main.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_submit_complaint(monkeypatch):
    client = TestClient(main.app)
    monkeypatch.setattr(main, "get_plugin", lambda agency: DummyPlugin())

    payload = {
        "agency": "fcc",
        "phoneNumber": "+15555551234",
        "description": "Robocall complaint",
        "timestamp": "2026-01-01T12:00:00Z",
    }

    response = client.post("/complaints", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["received"] is True
    assert body["state"] == "submitted"
    assert body["id"]


def test_complaint_status(monkeypatch):
    client = TestClient(main.app)
    monkeypatch.setattr(main, "get_plugin", lambda agency: DummyPlugin())

    payload = {
        "agency": "fcc",
        "phoneNumber": "+15555551234",
        "description": "Status lookup complaint",
        "timestamp": "2026-01-01T12:00:00Z",
    }

    submit_response = client.post("/complaints", json=payload)
    complaint_id = submit_response.json()["id"]

    status_response = client.get(f"/complaints/{complaint_id}")

    assert status_response.status_code == 200
    assert status_response.json() == {
        "id": complaint_id,
        "state": "submitted",
        "agency": "fcc",
        "agency_reference": "REF-123",
    }
