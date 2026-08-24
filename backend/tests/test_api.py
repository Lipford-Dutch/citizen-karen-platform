def test_health_is_versioned(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-request-id"]


def test_submit_track_and_delete_local_copy(client, complaint_payload):
    submitted = client.post("/api/complaints", json=complaint_payload)

    assert submitted.status_code == 201
    receipt = submitted.json()
    assert receipt["tracking_id"].startswith("CK-")
    assert receipt["state"] == "submitted"
    assert receipt["agency_reference"].startswith("FCC-")

    status = client.get(f"/api/complaints/{receipt['tracking_id'].lower()}")
    assert status.status_code == 200
    assert status.json()["tracking_id"] == receipt["tracking_id"]
    assert status.json()["complaint_type"] == "Unwanted calls or texts"
    assert status.json()["consent_version"] == "2026-08-23"

    deleted = client.delete(f"/api/complaints/{receipt['tracking_id']}")
    assert deleted.status_code == 200
    assert deleted.json()["state"] == "deleted"

    redacted = client.get(f"/api/complaints/{receipt['tracking_id']}")
    assert redacted.json()["state"] == "deleted"
    assert redacted.json()["complaint_type"] == "[deleted]"
    assert redacted.headers["cache-control"] == "no-store"


def test_consent_is_required(client, complaint_payload):
    complaint_payload["consent"] = False

    response = client.post("/api/complaints", json=complaint_payload)

    assert response.status_code == 422
    assert "Consent is required" in response.text


def test_sensitive_numbers_are_rejected(client, complaint_payload):
    complaint_payload["description"] = (
        "A caller asked me to confirm Social Security number 123-45-6789."
    )

    response = client.post("/api/complaints", json=complaint_payload)

    assert response.status_code == 422
    assert "Remove Social Security" in response.text


def test_unavailable_direct_connector_points_to_official_portal(
    client, complaint_payload
):
    complaint_payload["agency"] = "cfpb"

    response = client.post("/api/complaints", json=complaint_payload)

    assert response.status_code == 400
    assert "official portal" in response.json()["detail"]


def test_missing_tracking_id_returns_404(client):
    response = client.get("/api/complaints/CK-2026-MISSING")

    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"


def test_metrics_do_not_use_tracking_ids_as_labels(client, complaint_payload):
    receipt = client.post("/api/complaints", json=complaint_payload).json()
    client.get(f"/api/complaints/{receipt['tracking_id']}")

    metrics = client.get("/metrics")

    assert metrics.status_code == 200
    assert "/api/complaints/{tracking_id}" in metrics.text
    assert receipt["tracking_id"] not in metrics.text
