from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict

from app.plugins.registry import get_plugin

app = FastAPI(title="Citizen Karen API", version="1.0.0")

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

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/complaints", response_model=ComplaintOut, status_code=201)
async def submit_complaint(complaint: ComplaintIn):
    cid = str(uuid4())
    plugin = get_plugin(complaint.agency)

    upstream = await plugin.submit(complaint.dict())

    record = {
        "id": cid,
        "state": upstream.get("state", "pending"),
        "agency": complaint.agency,
        "agency_reference": upstream.get("agency_reference"),
    }
    complaints_store[cid] = record

    return ComplaintOut(id=cid, received=True, state=record["state"])

@app.get("/complaints/{cid}")
async def get_status(cid: str):
    if cid not in complaints_store:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaints_store[cid]

