# backend/app/main.py
from fastapi import FastAPI
from .db import init_db
from .api.complaints import router as complaints_router
from .metrics import prometheus_app
import uvicorn
import os

app = FastAPI(
    title="Karing USA API",
    version="0.1.0",
    openapi_url="/openapi.json"
)

app.include_router(complaints_router, prefix="/api")
app.include_router(prometheus_app(), prefix="/")

@app.on_event("startup")
def on_startup():
    init_db()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
