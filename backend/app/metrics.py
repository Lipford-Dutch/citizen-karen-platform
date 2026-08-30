# backend/app/metrics.py
from fastapi import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Latency of requests", ["endpoint"]
)
REQUEST_COUNT = Counter("request_count", "Total request count", ["endpoint", "method"])
AGENCY_SUBMISSION = Counter(
    "agency_submission_total",
    "Agency plugin submission outcomes",
    ["agency", "status", "error_class"],
)
AGENCY_LATENCY = Histogram(
    "agency_submission_duration_seconds",
    "Agency plugin submission latency",
    ["agency"],
)
CELERY_TASKS = Counter(
    "celery_task_total", "Background task outcomes", ["task", "status"]
)
QUEUE_DEPTH = Gauge("celery_queue_depth", "Approximate queued demo tasks")
EVIDENCE_SCAN = Counter("evidence_scan_total", "Evidence scan outcomes", ["status"])


def track(endpoint: str, method: str):
    REQUEST_COUNT.labels(endpoint=endpoint, method=method).inc()
    return REQUEST_LATENCY.labels(endpoint=endpoint)


def prometheus_app():
    from fastapi import APIRouter

    router = APIRouter()

    @router.get("/metrics")
    def metrics():
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    return router
