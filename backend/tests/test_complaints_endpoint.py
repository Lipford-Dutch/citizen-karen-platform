from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app import main


def test_submit_complaint_returns_tracking_id_and_invokes_plugin(monkeypatch):
    main.complaints_store.clear()
    captured = {}

    class DummyPlugin:
        async def submit(self, payload):
            captured["payload"] = payload
            return {"state": "submitted", "agency_reference": "ref-123"}

    monkeypatch.setattr(main, "get_plugin", lambda agency: DummyPlugin())
    client = TestClient(main.app)

    response = client.post(
        "/complaints",
        json={
            "agency": "fcc",
            "phoneNumber": "1234567890",
            "description": "Robocall complaint",
            "timestamp": "2026-08-23T23:00:00Z",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["tracking_id"]
    assert body["id"] == body["tracking_id"]
    assert body["received"] is True
    assert body["state"] == "submitted"
    assert captured["payload"]["agency"] == "fcc"


def test_submit_complaint_validates_timestamp_format():
    client = TestClient(main.app)

    response = client.post(
        "/complaints",
        json={
            "agency": "fcc",
            "phoneNumber": "1234567890",
            "description": "Robocall complaint",
            "timestamp": "not-a-timestamp",
        },
    )

    assert response.status_code == 422


def test_submit_complaint_returns_400_for_unknown_agency():
    client = TestClient(main.app)

    response = client.post(
        "/complaints",
        json={
            "agency": "unknown-agency",
            "phoneNumber": "1234567890",
            "description": "Test complaint",
            "timestamp": "2026-08-23T23:00:00Z",
        },
    )

    assert response.status_code == 400
    assert "No plugin registered for agency" in response.json()["detail"]
