import io

from app import auth, main


def _login(client, role="citizen"):
    response = client.post(f"/api/auth/demo/{role}")
    assert response.status_code == 200
    return response.json()["access_token"]


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_liveness_readiness_and_plugin_contract(client):
    assert client.get("/health/live").json() == {"status": "alive"}
    assert client.get("/health/ready").json()["database"] == "connected"
    catalog = client.get("/api/plugins").json()
    assert len(catalog["plugins"]) == 8
    assert all(item["simulated"] for item in catalog["plugins"])

    schema = client.get("/api/plugins/irs/schema")
    assert schema.status_code == 200
    assert schema.json()["compliance"]["kyc_level"] == "high"
    assert client.get("/api/plugins/unknown/schema").status_code == 404


def test_demo_auth_roles_and_invalid_tokens(client, monkeypatch):
    citizen = client.post("/api/auth/demo/citizen")
    assert citizen.json()["user"]["role"] == "citizen"
    assert client.post("/api/auth/demo/nope").status_code == 400
    assert (
        client.get(
            "/api/complaints", headers={"Authorization": "Bearer invalid"}
        ).status_code
        == 401
    )

    monkeypatch.setenv("DEMO_MODE", "false")
    assert client.get("/api/auth/demo-users").status_code == 404
    assert client.post("/api/auth/demo/citizen").status_code == 404
    monkeypatch.setenv("DEMO_MODE", "true")


def test_case_listing_retry_escalation_and_admin(client, complaint_payload):
    citizen_token = _login(client)
    submitted = client.post(
        "/api/complaints", json=complaint_payload, headers=_headers(citizen_token)
    ).json()
    tracking_id = submitted["tracking_id"]

    anonymous_cases = client.get("/api/complaints").json()["cases"]
    assert anonymous_cases == []
    citizen_cases = client.get(
        "/api/complaints", headers=_headers(citizen_token)
    ).json()["cases"]
    assert [item["tracking_id"] for item in citizen_cases] == [tracking_id]

    retry = client.post(f"/api/complaints/{tracking_id}/retry")
    assert retry.json()["state"] == "retrying"
    escalated = client.post(f"/api/complaints/{tracking_id}/escalate")
    assert escalated.json()["state"] == "escalated"
    assert client.post("/api/complaints/missing/retry").status_code == 404
    assert client.post("/api/complaints/missing/escalate").status_code == 404

    assert (
        client.get("/api/admin/operations", headers=_headers(citizen_token)).status_code
        == 403
    )
    admin_token = _login(client, "admin")
    operations = client.get("/api/admin/operations", headers=_headers(admin_token))
    assert operations.status_code == 200
    assert operations.json()["counts"]["total"] == 1


def test_evidence_scan_and_retention(client, complaint_payload):
    tracking_id = client.post("/api/complaints", json=complaint_payload).json()[
        "tracking_id"
    ]
    accepted = client.post(
        f"/api/complaints/{tracking_id}/evidence",
        files={
            "evidence": ("proof.txt", io.BytesIO(b"synthetic evidence"), "text/plain")
        },
    )
    assert accepted.status_code == 200
    assert accepted.json()["scan_status"] == "clean"
    assert accepted.json()["retention_days"] == 30

    blocked = client.post(
        f"/api/complaints/{tracking_id}/evidence",
        files={
            "evidence": (
                "eicar.txt",
                io.BytesIO(b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE"),
                "text/plain",
            )
        },
    )
    assert blocked.status_code == 422
    unsupported = client.post(
        f"/api/complaints/{tracking_id}/evidence",
        files={"evidence": ("demo.exe", io.BytesIO(b"x"), "application/octet-stream")},
    )
    assert unsupported.status_code == 415
    too_large = client.post(
        f"/api/complaints/{tracking_id}/evidence",
        files={"evidence": ("large.txt", io.BytesIO(b"x" * 5_000_001), "text/plain")},
    )
    assert too_large.status_code == 413
    assert (
        client.post(
            "/api/complaints/missing/evidence",
            files={"evidence": ("proof.txt", io.BytesIO(b"x"), "text/plain")},
        ).status_code
        == 404
    )


def test_kyc_and_failure_lab_outcomes(client, complaint_payload):
    assert client.get("/api/kyc/check/irs").json()["required_level"] == "high"
    assert client.get("/api/kyc/check/nope").status_code == 404

    complaint_payload["agency"] = "failure-lab"
    complaint_payload["complaint_type"] = "Retry path"
    retry = client.post("/api/complaints", json=complaint_payload)
    assert retry.json()["state"] == "retrying"

    complaint_payload["complaint_type"] = "Permanent failure"
    failure = client.post("/api/complaints", json=complaint_payload)
    assert failure.json()["state"] == "needs_attention"

    complaint_payload["complaint_type"] = "Escalation path"
    escalation = client.post("/api/complaints", json=complaint_payload)
    assert escalation.json()["state"] == "needs_attention"


def test_velocity_control(client, complaint_payload, monkeypatch):
    monkeypatch.setenv("SUBMISSION_RATE_LIMIT_PER_MINUTE", "1")
    main._velocity.clear()
    assert client.post("/api/complaints", json=complaint_payload).status_code == 201
    assert client.post("/api/complaints", json=complaint_payload).status_code == 429
    main._velocity.clear()
    monkeypatch.setenv("SUBMISSION_RATE_LIMIT_PER_MINUTE", "5")


def test_auth_helpers_reject_non_admin():
    assert auth.optional_user(None) is None
