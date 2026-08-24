# backend/app/metrics.py
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Latency of requests", ["endpoint"]
)
REQUEST_COUNT = Counter("request_count", "Total request count", ["endpoint", "method"])


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
