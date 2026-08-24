import os
import secrets
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from .db import ComplaintStore
from .logging_config import get_logger
from .metrics import prometheus_app, track
from .models import (
    ComplaintCreated,
    ComplaintState,
    ComplaintStatus,
    ComplaintSubmission,
    DeletionResponse,
)
from .plugins.registry import get_plugin

VERSION = "1.0.0"
logger = get_logger()
store = ComplaintStore(
    os.getenv(
        "CITIZEN_KAREN_DB_PATH",
        str(Path(__file__).resolve().parents[1] / "data" / "citizen-karen.db"),
    )
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    store.init()
    yield


app = FastAPI(
    title="Citizen Karen API",
    description="Consent-first intake and tracking for civic complaints.",
    version=VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or secrets.token_hex(8)
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    route = request.scope.get("route")
    metric_path = getattr(route, "path", request.url.path)
    track(metric_path, request.method).observe(time.perf_counter() - started)
    logger.info(
        "request_finished",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        },
    )
    return response


router = APIRouter(prefix="/api")


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": VERSION}


@router.post(
    "/complaints",
    response_model=ComplaintCreated,
    status_code=status.HTTP_201_CREATED,
    tags=["Complaints"],
)
async def submit_complaint(payload: ComplaintSubmission) -> ComplaintCreated:
    try:
        plugin = get_plugin(payload.agency)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    complaint_id = str(uuid4())
    tracking_id = f"CK-{datetime.now(UTC).year}-{secrets.token_hex(3).upper()}"
    record = store.create(
        complaint_id=complaint_id,
        tracking_id=tracking_id,
        submission=payload,
    )
    upstream = await plugin.submit(
        payload.model_dump(mode="json", exclude={"consent", "website"})
    )
    record = (
        store.mark_submitted(
            tracking_id,
            agency_reference=upstream.get("agency_reference"),
            state=upstream.get("state", "submitted"),
        )
        or record
    )
    logger.info(
        "complaint_submitted",
        extra={"tracking_id": tracking_id, "agency": payload.agency},
    )
    return _created(record)


@router.get(
    "/complaints/{tracking_id}",
    response_model=ComplaintStatus,
    tags=["Complaints"],
)
def get_status(tracking_id: str) -> ComplaintStatus:
    record = store.get(tracking_id.strip().upper())
    if not record:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return _status(record)


@router.delete(
    "/complaints/{tracking_id}",
    response_model=DeletionResponse,
    tags=["Privacy"],
)
def delete_complaint_copy(tracking_id: str) -> DeletionResponse:
    normalized = tracking_id.strip().upper()
    record = store.get(normalized)
    if not record:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if record["status"] == ComplaintState.DELETED:
        return DeletionResponse(tracking_id=normalized)
    if not store.delete_copy(normalized):
        raise HTTPException(status_code=409, detail="Complaint could not be deleted")
    logger.info("complaint_copy_deleted", extra={"tracking_id": normalized})
    return DeletionResponse(tracking_id=normalized)


def _created(record: dict) -> ComplaintCreated:
    return ComplaintCreated(
        id=record["id"],
        tracking_id=record["tracking_id"],
        state=record["status"],
        agency=record["agency"],
        agency_reference=record["agency_reference"],
        submitted_at=record["submitted_at"],
    )


def _status(record: dict) -> ComplaintStatus:
    return ComplaintStatus(
        id=record["id"],
        tracking_id=record["tracking_id"],
        state=record["status"],
        agency=record["agency"],
        agency_reference=record["agency_reference"],
        complaint_type=record["complaint_type"],
        submitted_at=record["submitted_at"],
        last_updated=record["last_updated"],
        consent_version=record["consent_version"],
    )


app.include_router(router)
app.include_router(prometheus_app())
