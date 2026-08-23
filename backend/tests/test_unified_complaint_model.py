from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.complaint_model import ComplaintSubmission, NormalizedComplaint  # noqa: E402
from app.main import app  # noqa: E402


def test_normalizes_legacy_ui_payload():
    payload = ComplaintSubmission(
        name="Citizen",
        email="citizen@example.com",
        description="robocall spam",
        agency_hint="fcc",
    )
    normalized = NormalizedComplaint.from_submission(payload)

    assert normalized.agency == "fcc"
    plugin_payload = normalized.to_plugin_payload()
    assert plugin_payload["agency"] == "fcc"
    assert plugin_payload["agency_hint"] == "fcc"
    assert plugin_payload["description"] == "robocall spam"


def test_accepts_api_shape_phone_number_alias():
    payload = ComplaintSubmission(
        agency="fcc",
        phoneNumber="+15551234567",
        description="test",
        timestamp="2026-01-01T00:00:00Z",
    )

    assert payload.phone_number == "+15551234567"
    assert payload.agency == "fcc"


def test_submit_endpoint_accepts_ui_payload(monkeypatch):
    captured = {}

    class StubPlugin:
        async def submit(self, complaint):
            captured["payload"] = complaint
            return {"state": "submitted", "agency_reference": "abc-123"}

    monkeypatch.setattr("app.main.get_plugin", lambda agency: StubPlugin())

    client = TestClient(app)
    response = client.post(
        "/complaints",
        json={
            "name": "Citizen",
            "email": "citizen@example.com",
            "description": "robocall spam",
            "agency_hint": "fcc",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["received"] is True
    assert body["state"] == "submitted"
    assert body["id"]
    assert captured["payload"]["agency"] == "fcc"
