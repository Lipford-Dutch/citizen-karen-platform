import os

from celery import Celery

broker = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery(
    "citizen_karen", broker=broker, backend=broker, include=["app.tasks"]
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
    beat_schedule={
        "poll-active-cases": {"task": "citizen_karen.poll_active", "schedule": 60.0},
        "escalation-scan": {"task": "citizen_karen.escalation_scan", "schedule": 120.0},
    },
)
