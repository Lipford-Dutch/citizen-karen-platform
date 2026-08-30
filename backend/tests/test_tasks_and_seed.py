import smtplib

import anyio

from app import seed as seed_module
from app import tasks
from app.db import ComplaintStore
from app.models import ComplaintSubmission


def test_seed_is_deterministic(tmp_path, monkeypatch):
    database_url = f"sqlite:///{(tmp_path / 'seed.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    assert seed_module.seed() == 8
    assert seed_module.seed() == 0
    store = ComplaintStore(database_url)
    assert len(store.list_cases(owner_id="demo-citizen")) == 8
    assert store.get("CK-DEMO-LAB-007")["retry_count"] == 1
    store.engine.dispose()


def test_actual_submission_task_helper(tmp_path, monkeypatch):
    database_url = f"sqlite:///{(tmp_path / 'task.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("FCC_CONNECTOR_MODE", "simulate")
    store = ComplaintStore(database_url)
    store.init()
    store.create(
        complaint_id="task-id",
        tracking_id="CK-TASK-001",
        submission=ComplaintSubmission(
            agency="fcc",
            full_name="Demo Citizen",
            email="demo@example.com",
            complaint_type="Unwanted calls",
            description="Synthetic complaint used to exercise the worker helper.",
            consent=True,
        ),
    )
    result = anyio.run(tasks._submit, "CK-TASK-001")
    assert result["status"] == "submitted"
    store.engine.dispose()


class FakeStore:
    def __init__(self, status="submitted"):
        self.status = status
        self.transitions = []

    def get(self, tracking_id):
        if tracking_id == "missing":
            return None
        return {"tracking_id": tracking_id, "agency": "fcc", "status": self.status}

    def transition(self, *args, **kwargs):
        self.transitions.append((args, kwargs))
        return {"status": kwargs.get("state", "retrying")}

    def list_cases(self, limit=200):
        return [
            {"status": "submitted"},
            {"status": "under_review"},
            {"status": "needs_attention"},
            {"status": "resolved"},
        ]


def test_task_success_failure_polling_and_escalation(monkeypatch):
    fake = FakeStore()
    monkeypatch.setattr(tasks, "_store", lambda: fake)

    async def success(_tracking_id):
        return {"status": "submitted"}

    monkeypatch.setattr(tasks, "_submit", success)
    monkeypatch.setattr(tasks.send_confirmation, "delay", lambda *_: None)
    assert tasks.submit_complaint_task.run("CK-1")["status"] == "submitted"

    async def failure(_tracking_id):
        raise ValueError("permanent")

    monkeypatch.setattr(tasks, "_submit", failure)
    assert tasks.submit_complaint_task.run("CK-2")["state"] == "needs_attention"
    assert fake.transitions

    async def timeout(_tracking_id):
        raise TimeoutError("retryable")

    monkeypatch.setattr(tasks, "_submit", timeout)
    tasks.submit_complaint_task.push_request(retries=3)
    try:
        exhausted = tasks.submit_complaint_task.run("CK-3")
    finally:
        tasks.submit_complaint_task.pop_request()
    assert exhausted["state"] == "needs_attention"
    assert tasks.poll_active.run()["candidates"] == 2
    assert tasks.escalation_scan.run()["candidates"] == 1


def test_confirmation_capture_success_missing_and_failure(monkeypatch):
    fake = FakeStore()
    monkeypatch.setattr(tasks, "_store", lambda: fake)

    class FakeSMTP:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def sendmail(self, sender, recipients, message):
            assert sender.endswith(".local")
            assert recipients == ["karen@example.test"]
            assert "not a government acknowledgement" in message

    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    assert tasks.send_confirmation.run("CK-1")["status"] == "captured"
    assert tasks.send_confirmation.run("missing")["status"] == "missing"

    class BrokenSMTP(FakeSMTP):
        def __enter__(self):
            raise OSError("offline")

    monkeypatch.setattr(smtplib, "SMTP", BrokenSMTP)
    assert tasks.send_confirmation.run("CK-1")["status"] == "mail_capture_unavailable"
