# backend/app/main.py
import time
import uuid as _uuid

from fastapi import FastAPI, Request
from .db import init_db
from .api.complaints import router as complaints_router
from .metrics import prometheus_app
from .logging_config import get_logger
import uvicorn
import os

logger = get_logger()

app = FastAPI(
    title="Karing USA API",
    version="0.1.0",
    openapi_url="/openapi.json"
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(_uuid.uuid4())
    start = time.time()
    logger.info(
        "request_started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None,
        },
    )
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(
            "request_failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error": str(exc),
            },
        )
        raise
    duration_ms = round((time.time() - start) * 1000, 2)
    logger.info(
        "request_finished",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


app.include_router(complaints_router, prefix="/api")
app.include_router(prometheus_app(), prefix="/")


@app.on_event("startup")
def on_startup():
    init_db()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
