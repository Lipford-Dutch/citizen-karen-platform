import os
import secrets
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware

from .auth import DEMO_USERS, issue_demo_token, optional_user, require_admin
from .db import ComplaintStore, EvidenceRecord
from .logging_config import get_logger
from .metrics import (
    AGENCY_LATENCY,
    AGENCY_SUBMISSION,
    EVIDENCE_SCAN,
    prometheus_app,
    track,
)
from .models import (
    ComplaintCreated,
    ComplaintState,
    ComplaintStatus,
    ComplaintSubmission,
    DeletionResponse,
)
from .observability import configure_observability
from .plugins.base import DISCLAIMER
from .plugins.registry import get_plugin, list_plugins

VERSION = "1.0.0-rc.2"
logger = get_logger()
store = ComplaintStore(
    os.getenv("DATABASE_URL")
    or os.getenv(
        "CITIZEN_KAREN_DB_PATH",
        str(Path(__file__).resolve().parents[1] / "data" / "citizen-karen.db"),
    )
)
_velocity: dict[str, deque[float]] = defaultdict(deque)


@asynccontextmanager
async def lifespan(_: FastAPI):
    store.init()
    yield


app = FastAPI(
    title="Citizen Karen API",
    description=(
        "Consent-first intake and tracking for civic complaints. Citizen Karen is "
        "not a government service or legal advice. Demo integrations are simulated."
    ),
    version=VERSION,
    openapi_version="3.1.0",
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
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
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
    response.headers["X-Citizen-Karen-Disclaimer"] = DISCLAIMER
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


@app.get("/health/live", tags=["System"])
def live() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/ready", tags=["System"])
def ready() -> dict[str, str]:
    if not store.ready():
        raise HTTPException(
            status_code=503, detail="Source-of-truth database unavailable"
        )
    return {"status": "ready", "database": "connected"}


@router.get("/plugins", tags=["Agency plugins"])
def plugin_catalog() -> dict[str, Any]:
    return {
        "plugins": [plugin.manifest.__dict__ for plugin in list_plugins()],
        "disclaimer": DISCLAIMER,
    }


@router.get("/plugins/{agency}/schema", tags=["Agency plugins"])
def plugin_schema(agency: str) -> dict[str, Any]:
    try:
        manifest = get_plugin(agency).manifest
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "agency": manifest.key,
        "schema": manifest.form_schema,
        "compliance": {
            "automation": manifest.automation,
            "simulated": manifest.simulated,
            "restrictions": manifest.restrictions,
            "kyc_level": manifest.kyc_level,
        },
        "disclaimer": DISCLAIMER,
    }


@router.get("/auth/demo-users", tags=["Demo authentication"])
def demo_users() -> dict[str, Any]:
    if os.getenv("DEMO_MODE", "true").lower() != "true":
        raise HTTPException(status_code=404, detail="Demo mode disabled")
    return {"users": list(DEMO_USERS.values()), "disclaimer": DISCLAIMER}


@router.post("/auth/demo/{role}", tags=["Demo authentication"])
def demo_login(role: str) -> dict[str, Any]:
    return issue_demo_token(role)


def _check_velocity(request: Request) -> None:
    key = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = _velocity[key]
    while window and now - window[0] > 60:
        window.popleft()
    limit = int(os.getenv("SUBMISSION_RATE_LIMIT_PER_MINUTE", "5"))
    if len(window) >= limit:
        raise HTTPException(status_code=429, detail="Submission rate limit exceeded")
    window.append(now)


@router.post(
    "/complaints",
    response_model=ComplaintCreated,
    status_code=status.HTTP_201_CREATED,
    tags=["Complaints"],
)
async def submit_complaint(
    payload: ComplaintSubmission,
    request: Request,
    user: Annotated[dict[str, Any] | None, Depends(optional_user)],
) -> ComplaintCreated:
    _check_velocity(request)
    try:
        plugin = get_plugin(payload.agency)
        plugin.validate(payload.model_dump(mode="json"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    complaint_id = str(uuid4())
    tracking_id = f"CK-{datetime.now(UTC).year}-{secrets.token_hex(3).upper()}"
    record = store.create(
        complaint_id=complaint_id,
        tracking_id=tracking_id,
        submission=payload,
        owner_id=user.get("sub") if user else None,
    )
    if os.getenv("ASYNC_SUBMISSIONS", "false").lower() == "true":
        from .metrics import QUEUE_DEPTH
        from .tasks import submit_complaint_task

        QUEUE_DEPTH.inc()
        submit_complaint_task.delay(tracking_id)
    else:
        try:
            with AGENCY_LATENCY.labels(agency=payload.agency).time():
                upstream = await plugin.submit(
                    payload.model_dump(mode="json", exclude={"consent", "website"})
                )
            AGENCY_SUBMISSION.labels(
                agency=payload.agency, status="success", error_class="none"
            ).inc()
            record = (
                store.mark_submitted(
                    tracking_id,
                    agency_reference=upstream.get("agency_reference"),
                    state=upstream.get("state", "submitted"),
                )
                or record
            )
        except TimeoutError:
            AGENCY_SUBMISSION.labels(
                agency=payload.agency, status="retry", error_class="timeout"
            ).inc()
            record = (
                store.transition(
                    tracking_id,
                    "retrying",
                    event_type="submission_retry_scheduled",
                    failure_code="upstream_timeout",
                    increment_retry=True,
                )
                or record
            )
            logger.warning(
                "submission_retry_scheduled",
                extra={"tracking_id": tracking_id, "agency": payload.agency},
            )
        except Exception as exc:  # noqa: BLE001 - plugin boundary normalizes failures
            AGENCY_SUBMISSION.labels(
                agency=payload.agency,
                status="failure",
                error_class=type(exc).__name__,
            ).inc()
            record = (
                store.transition(
                    tracking_id,
                    "needs_attention",
                    event_type="submission_failed",
                    failure_code=type(exc).__name__,
                )
                or record
            )
    logger.info(
        "complaint_accepted",
        extra={"tracking_id": tracking_id, "agency": payload.agency},
    )
    return _created(record)


@router.get("/complaints", tags=["Complaints"])
def list_cases(
    user: Annotated[dict[str, Any] | None, Depends(optional_user)],
) -> dict[str, Any]:
    owner = (
        None
        if user and user.get("role") == "admin"
        else (user or {}).get("sub", "__anonymous__")
    )
    return {"cases": store.list_cases(owner_id=owner), "disclaimer": DISCLAIMER}


@router.get(
    "/complaints/{tracking_id}", response_model=ComplaintStatus, tags=["Complaints"]
)
def get_status(tracking_id: str) -> ComplaintStatus:
    record = store.get(tracking_id.strip().upper())
    if not record:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return _status(record)


@router.post("/complaints/{tracking_id}/retry", tags=["Complaints"])
def retry_complaint(tracking_id: str) -> dict[str, Any]:
    normalized = tracking_id.strip().upper()
    record = store.get(normalized)
    if not record:
        raise HTTPException(status_code=404, detail="Complaint not found")
    store.transition(
        normalized,
        "retrying",
        event_type="manual_retry_requested",
        increment_retry=True,
    )
    if os.getenv("ASYNC_SUBMISSIONS", "false").lower() == "true":
        from .tasks import submit_complaint_task

        submit_complaint_task.delay(normalized)
    return {"tracking_id": normalized, "state": "retrying", "disclaimer": DISCLAIMER}


@router.post("/complaints/{tracking_id}/escalate", tags=["Complaints"])
def escalate_complaint(tracking_id: str) -> dict[str, Any]:
    normalized = tracking_id.strip().upper()
    if not store.get(normalized):
        raise HTTPException(status_code=404, detail="Complaint not found")
    store.transition(
        normalized,
        "escalated",
        event_type="manual_review_escalation_requested",
        metadata={"route": "demo_admin_queue"},
    )
    return {"tracking_id": normalized, "state": "escalated", "disclaimer": DISCLAIMER}


@router.post("/complaints/{tracking_id}/evidence", tags=["Evidence"])
async def upload_evidence(
    tracking_id: str,
    evidence: Annotated[UploadFile, File()],
) -> dict[str, Any]:
    normalized = tracking_id.strip().upper()
    if not store.get(normalized):
        raise HTTPException(status_code=404, detail="Complaint not found")
    allowed = {"application/pdf", "image/png", "image/jpeg", "text/plain"}
    if evidence.content_type not in allowed:
        raise HTTPException(status_code=415, detail="Unsupported evidence type")
    content = await evidence.read(5_000_001)
    if len(content) > 5_000_000:
        raise HTTPException(status_code=413, detail="Evidence exceeds 5 MB demo limit")
    scan_status = (
        "blocked" if b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE" in content else "clean"
    )
    EVIDENCE_SCAN.labels(status=scan_status).inc()
    if scan_status == "blocked":
        raise HTTPException(status_code=422, detail="Evidence failed malware scan stub")
    now = datetime.now(UTC)
    evidence_id = str(uuid4())
    store.add_evidence(
        EvidenceRecord(
            id=evidence_id,
            tracking_id=normalized,
            filename=Path(evidence.filename or "evidence").name,
            content_type=evidence.content_type or "application/octet-stream",
            size_bytes=len(content),
            scan_status=scan_status,
            retention_until=now + timedelta(days=30),
            content=content,
            created_at=now,
        )
    )
    return {
        "id": evidence_id,
        "scan_status": scan_status,
        "retention_days": 30,
        "storage": "local encrypted-volume boundary (demo)",
        "disclaimer": DISCLAIMER,
    }


@router.get("/kyc/check/{agency}", tags=["Safety controls"])
def kyc_check(agency: str) -> dict[str, Any]:
    try:
        manifest = get_plugin(agency).manifest
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "agency": agency,
        "required_level": manifest.kyc_level,
        "status": "demo_stub",
        "checks": ["email", "phone"] if manifest.kyc_level != "low" else ["email"],
        "disclaimer": DISCLAIMER,
    }


@router.get("/admin/operations", tags=["Admin demo"])
def admin_operations(
    user: Annotated[dict[str, Any] | None, Depends(optional_user)],
) -> dict[str, Any]:
    require_admin(user)
    cases = store.list_cases(limit=500)
    return {
        "counts": {
            "total": len(cases),
            "needs_attention": sum(
                case["status"] == "needs_attention" for case in cases
            ),
            "retrying": sum(case["status"] == "retrying" for case in cases),
        },
        "queue": {"mode": "celery_redis", "status": "simulated_local_demo"},
        "disclaimer": DISCLAIMER,
    }


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


def _created(record: dict[str, Any]) -> ComplaintCreated:
    return ComplaintCreated(
        id=record["id"],
        tracking_id=record["tracking_id"],
        state=record["status"],
        agency=record["agency"],
        agency_reference=record["agency_reference"],
        submitted_at=record["submitted_at"],
    )


def _status(record: dict[str, Any]) -> ComplaintStatus:
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
        events=record.get("events", []),
        retry_count=record.get("retry_count", 0),
        next_action_at=record.get("next_action_at"),
    )


app.include_router(router)
app.include_router(prometheus_app())
configure_observability(app, store.engine)
