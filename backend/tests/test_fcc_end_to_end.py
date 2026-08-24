import pathlib
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.main import app, complaints_store


class DummyFccPlugin:
    async def submit(self, complaint):
        return {"state": "submitted", "agency_reference": "FCC-E2E-001"}


def test_fcc_submit_and_get_status_end_to_end(monkeypatch):
    complaints_store.clear()
    monkeypatch.setattr("app.main.get_plugin", lambda agency: DummyFccPlugin())

    client = TestClient(app)

    submit_response = client.post(
        "/complaints",
        json={
            "agency": "fcc",
            "phoneNumber": "555-1212",
            "description": "Robocall complaint",
            "timestamp": "2026-08-24T00:00:00Z",
        },
    )
    assert submit_response.status_code == 201
    body = submit_response.json()
    assert body["received"] is True
    assert body["state"] == "submitted"
    assert body["id"]

    complaint_id = body["id"]
    status_response = client.get(f"/complaints/{complaint_id}")
    assert status_response.status_code == 200
    status_body = status_response.json()
    assert status_body["id"] == complaint_id
    assert status_body["agency"] == "fcc"
    assert status_body["state"] == "submitted"
    assert status_body["agency_reference"] == "FCC-E2E-001"
