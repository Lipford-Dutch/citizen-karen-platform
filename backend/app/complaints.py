# backend/app/api/complaints.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import uuid
from sqlalchemy.orm import Session
from ..db import SessionLocal, Complaint
from ..plugins import sample_agency  # import your plugins
from ..logging_config import get_logger
from ..metrics import track

logger = get_logger()
router = APIRouter()

class ComplaintIn(BaseModel):
    # Example fields — adjust per your real data model
    name: str
    email: str
    description: str
    agency_hint: str = None  # optional hint

class ComplaintOut(BaseModel):
    tracking_id: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Load plugins
PLUGIN_INSTANCES = [sample_agency.SampleAgencyPlugin()]

@router.post("/complaints", response_model=ComplaintOut)
def submit_complaint(payload: ComplaintIn, db: Session = Depends(get_db)):
    with track("submit_complaint", "POST").time():
        data = payload.dict()
        tracking_id = str(uuid.uuid4())
        logger.info(
            "complaint_received",
            extra={"tracking_id": tracking_id, "agency_hint": data.get("agency_hint")},
        )
        cmp = Complaint(tracking_id=tracking_id, payload=data)
        db.add(cmp)
        db.commit()
        db.refresh(cmp)

        # Try to route
        for plugin in PLUGIN_INSTANCES:
            plugin_name = type(plugin).__name__
            try:
                if plugin.matches(data):
                    logger.info(
                        "plugin_call_started",
                        extra={"plugin": plugin_name, "tracking_id": tracking_id},
                    )
                    resp = plugin.forward(data)
                    if resp.get("success"):
                        cmp.agency = resp.get("agency_id")
                        cmp.status = "forwarded"
                        logger.info(
                            "plugin_call_succeeded",
                            extra={
                                "plugin": plugin_name,
                                "tracking_id": tracking_id,
                                "agency_id": resp.get("agency_id"),
                                "status": "forwarded",
                            },
                        )
                    else:
                        cmp.status = "failed_forward"
                        logger.warning(
                            "plugin_call_rejected",
                            extra={
                                "plugin": plugin_name,
                                "tracking_id": tracking_id,
                                "status": "failed_forward",
                            },
                        )
                    cmp.last_updated = __import__("datetime").datetime.utcnow()
                    db.add(cmp)
                    db.commit()
                    break
            except Exception as e:
                logger.error(
                    "plugin_call_error",
                    extra={"plugin": plugin_name, "error": str(e), "tracking_id": tracking_id},
                )
                # graceful: leave complaint in pending or failed state
                cmp.status = "pending"
                cmp.last_updated = __import__("datetime").datetime.utcnow()
                db.add(cmp)
                db.commit()
                break

        return ComplaintOut(tracking_id=tracking_id)

@router.get("/complaints/{tracking_id}")
def get_status(tracking_id: str, db: Session = Depends(get_db)):
    cmp = db.query(Complaint).filter_by(tracking_id=tracking_id).first()
    if not cmp:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "tracking_id": cmp.tracking_id,
        "status": cmp.status,
        "agency": cmp.agency,
        "submitted_at": cmp.submitted_at,
        "last_updated": cmp.last_updated
    }
