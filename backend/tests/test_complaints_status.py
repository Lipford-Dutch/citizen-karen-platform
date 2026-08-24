from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app, complaints_store


client = TestClient(app)


def setup_function():
    complaints_store.clear()


def test_get_complaint_status_returns_state_and_agency_reference():
    complaints_store["abc-123"] = {
        "id": "abc-123",
        "state": "submitted",
        "agency": "fcc",
        "agency_reference": "FCC-REF-001",
    }

    response = client.get("/complaints/abc-123")

    assert response.status_code == 200
    assert response.json() == {
        "id": "abc-123",
        "state": "submitted",
        "agencyReference": "FCC-REF-001",
    }


def test_get_complaint_status_returns_404_when_missing():
    response = client.get("/complaints/missing-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"
