from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict
from datetime import datetime

from app.plugins.registry import get_plugin

app = FastAPI(title="Citizen Karen API", version="1.0.0")

class ComplaintIn(BaseModel):
    agency: str
    phoneNumber: str
    description: str
    timestamp: datetime

class ComplaintOut(BaseModel):
    id: str
    tracking_id: str
    received: bool
    state: str

# Temporary in-memory store (will be DB-backed later)
complaints_store: Dict[str, Dict] = {}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/complaints", response_model=ComplaintOut, status_code=201)
async def submit_complaint(complaint: ComplaintIn):
    cid = str(uuid4())
    try:
        plugin = get_plugin(complaint.agency)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    upstream = await plugin.submit(complaint.model_dump(mode="json"))

    record = {
        "id": cid,
        "state": upstream.get("state", "pending"),
        "agency": complaint.agency,
        "agency_reference": upstream.get("agency_reference"),
    }
    complaints_store[cid] = record

    return ComplaintOut(id=cid, tracking_id=cid, received=True, state=record["state"])

@app.get("/complaints/{cid}")
async def get_status(cid: str):
    if cid not in complaints_store:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaints_store[cid]
