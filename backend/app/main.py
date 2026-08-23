from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict

from app.api.health import router as health_router
from app.logging_config import get_logger

app = FastAPI(title="Citizen Karen API", version="1.0.0")
logger = get_logger()
app.include_router(health_router)

class ComplaintIn(BaseModel):
    agency: str
    phoneNumber: str
    description: str
    timestamp: str  # ISO8601

class ComplaintOut(BaseModel):
    id: str
    received: bool
    state: str

# Temporary in-memory store (will be DB-backed later)
complaints_store: Dict[str, Dict] = {}

@app.post("/complaints", response_model=ComplaintOut, status_code=201)
async def submit_complaint(complaint: ComplaintIn):
    cid = str(uuid4())
    from app.plugins.registry import get_plugin
    plugin = get_plugin(complaint.agency)

    upstream = await plugin.submit(complaint.dict())

    record = {
        "id": cid,
        "state": upstream.get("state", "pending"),
        "agency": complaint.agency,
        "agency_reference": upstream.get("agency_reference"),
    }
    complaints_store[cid] = record
    logger.info("Complaint received", extra={"complaint_id": cid, "agency": complaint.agency})

    return ComplaintOut(id=cid, received=True, state=record["state"])

@app.get("/complaints/{cid}")
async def get_status(cid: str):
    if cid not in complaints_store:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaints_store[cid]
