import asyncio
import os
import smtplib
from functools import lru_cache
from typing import Any

from .celery_app import celery_app
from .db import ComplaintStore
from .logging_config import get_logger
from .metrics import AGENCY_LATENCY, AGENCY_SUBMISSION, CELERY_TASKS, QUEUE_DEPTH
from .plugins.registry import get_plugin

logger = get_logger()


@lru_cache(maxsize=1)
def _store() -> ComplaintStore:
    store = ComplaintStore()
    store.init()
    return store


async def _submit(tracking_id: str) -> dict[str, Any]:
    store = _store()
    record = store.get(tracking_id)
    if not record:
        raise ValueError("Complaint no longer exists")
    plugin = get_plugin(record["agency"])
    import json

    payload = json.loads(record["payload_json"])
    with AGENCY_LATENCY.labels(agency=record["agency"]).time():
        upstream = await plugin.submit(payload)
    return (
        store.mark_submitted(
            tracking_id,
            agency_reference=upstream.get("agency_reference"),
            state=upstream.get("state", "submitted"),
        )
        or {}
    )


@celery_app.task(bind=True, name="citizen_karen.submit", max_retries=3)
def submit_complaint_task(self, tracking_id: str) -> dict[str, Any]:
    QUEUE_DEPTH.dec()
    record = _store().get(tracking_id) or {}
    agency = record.get("agency", "unknown")
    try:
        result = asyncio.run(_submit(tracking_id))
        AGENCY_SUBMISSION.labels(
            agency=agency, status="success", error_class="none"
        ).inc()
        CELERY_TASKS.labels(task="submit", status="success").inc()
        send_confirmation.delay(tracking_id)
        return result
    except TimeoutError as exc:
        store = _store()
        if self.request.retries >= self.max_retries:
            store.transition(
                tracking_id,
                "needs_attention",
                event_type="submission_retries_exhausted",
                failure_code="upstream_timeout",
                metadata={"attempts": self.request.retries + 1},
            )
            AGENCY_SUBMISSION.labels(
                agency=agency, status="failure", error_class="timeout_exhausted"
            ).inc()
            CELERY_TASKS.labels(task="submit", status="failure").inc()
            return {"tracking_id": tracking_id, "state": "needs_attention"}
        store.transition(
            tracking_id,
            "retrying",
            event_type="submission_retry_scheduled",
            failure_code="upstream_timeout",
            increment_retry=True,
            metadata={"attempt": self.request.retries + 1},
        )
        AGENCY_SUBMISSION.labels(
            agency=agency, status="retry", error_class="timeout"
        ).inc()
        CELERY_TASKS.labels(task="submit", status="retry").inc()
        raise self.retry(exc=exc, countdown=min(2 ** (self.request.retries + 1), 30))
    except Exception as exc:  # noqa: BLE001 - Celery plugin boundary records failures
        _store().transition(
            tracking_id,
            "needs_attention",
            event_type="submission_failed",
            failure_code=type(exc).__name__,
        )
        AGENCY_SUBMISSION.labels(
            agency=agency, status="failure", error_class=type(exc).__name__
        ).inc()
        CELERY_TASKS.labels(task="submit", status="failure").inc()
        logger.error(
            "submission_failed", extra={"tracking_id": tracking_id, "agency": agency}
        )
        return {"tracking_id": tracking_id, "state": "needs_attention"}


@celery_app.task(name="citizen_karen.poll_active")
def poll_active() -> dict[str, int]:
    candidates = [
        item
        for item in _store().list_cases(limit=200)
        if item["status"] in {"submitted", "under_review"}
    ]
    CELERY_TASKS.labels(task="poll_active", status="success").inc()
    return {"candidates": len(candidates)}


@celery_app.task(name="citizen_karen.escalation_scan")
def escalation_scan() -> dict[str, int]:
    candidates = [
        item
        for item in _store().list_cases(limit=200)
        if item["status"] == "needs_attention"
    ]
    CELERY_TASKS.labels(task="escalation_scan", status="success").inc()
    return {"candidates": len(candidates)}


@celery_app.task(name="citizen_karen.send_confirmation")
def send_confirmation(tracking_id: str) -> dict[str, str]:
    record = _store().get(tracking_id)
    if not record:
        return {"status": "missing"}
    message = (
        "From: demo@citizen-karen.local\r\n"
        "To: karen@example.test\r\n"
        f"Subject: Demo receipt {tracking_id}\r\n\r\n"
        "This local demo receipt is not a government acknowledgement or legal advice.\r\n"
        f"Tracking ID: {tracking_id}\r\n"
    )
    try:
        with smtplib.SMTP(
            os.getenv("SMTP_HOST", "mailhog"),
            int(os.getenv("SMTP_PORT", "1025")),
            timeout=5,
        ) as client:
            client.sendmail("demo@citizen-karen.local", ["karen@example.test"], message)
        CELERY_TASKS.labels(task="send_confirmation", status="success").inc()
        return {"status": "captured"}
    except OSError:
        CELERY_TASKS.labels(task="send_confirmation", status="failure").inc()
        return {"status": "mail_capture_unavailable"}
