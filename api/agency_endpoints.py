# backend/app/api/v1/agency_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.services.complaints_service import ComplaintsService

router = APIRouter(prefix="/api/v1", tags=["agencies"])

class ComplaintData(BaseModel):
    phone_number: str
    description: str
    timestamp: str

def _create_agency_endpoint(agency: str):
    async def agency_endpoint(
        complaint: ComplaintData, service: ComplaintsService = Depends(ComplaintsService)
    ):
        payload = complaint.dict()
        payload["agency"] = agency
        try:
            result = await service.submit_complaint(payload)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        return result

    return agency_endpoint

# Map URL path suffixes to agency identifiers (used by the plugin registry)
AGENCY_ENDPOINTS = {
    "doj-civil-rights": "doj_civil_rights",
    "cfpb-consumer": "cfpb",
    "usps": "usps",
    "eeoc": "eeoc",
    "cpsc": "cpsc",
    "dot-airline": "dot_airline",
    "nhtsa-vehicle": "nhtsa",
    "fda-food": "fda_food",
    "fda-drug-device": "fda_drug_device",
    "oig": "oig",
    "osc-whistleblower": "osc",
    "hhs-ocr": "hhs_ocr",
    "hud-housing": "hud",
    "doj-online-hate": "doj_online_hate",
    "fcc": "fcc",
    "sec-securities": "sec",
    "epa": "epa",
    "osha": "osha",
    "dol-wage-hour": "dol",
    "bop-prison": "bop",
    "cms-medicare-fraud": "cms",
    "ftc-privacy": "ftc",
    "ada-disability": "ada",
    "election-voting": "fec_doj_voting",
    "dod-military-sexual": "dod_military_sexual",
    "eeoc-federal": "eeoc_federal",
    "ice-detention": "ice",
    "fra-railroad": "fra",
    "fmcsa-maritime": "fmcsa",
}

# Register each endpoint dynamically
for path_suffix, agency_key in AGENCY_ENDPOINTS.items():
    endpoint_path = f"/complaints/{path_suffix}"
    endpoint = _create_agency_endpoint(agency_key)
    router.post(
        endpoint_path,
        name=f"submit_{path_suffix}_complaint",
        response_model=dict
    )(endpoint)