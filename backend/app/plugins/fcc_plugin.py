import os
import secrets

import httpx

from ..logging_config import get_logger
from .base import AgencyPlugin, PluginManifest

logger = get_logger()


class FccPlugin(AgencyPlugin):
    agency_name = "fcc"
    manifest = PluginManifest(
        key="fcc",
        name="Federal Communications Commission",
        short_name="FCC",
        version="2.0.0-demo",
        description="Phone, internet, television, radio, billing, and unwanted-call complaints.",
        official_url="https://consumercomplaints.fcc.gov/hc/en-us",
        category="Consumer",
        risk_score=44,
        risk_level="moderate",
        automation="Repository mock service or local simulation; no production endpoint is configured.",
        simulated=True,
        kyc_level="low",
        restrictions=("No restricted-portal login", "No CAPTCHA or MFA bypass"),
        form_schema={
            "title": "FCC complaint",
            "type": "object",
            "required": ["full_name", "email", "complaint_type", "description"],
            "properties": {
                "full_name": {
                    "type": "string",
                    "title": "Full name",
                    "minLength": 2,
                    "step": "About you",
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "title": "Email",
                    "step": "About you",
                },
                "phone_number": {
                    "type": "string",
                    "title": "Phone number",
                    "step": "About you",
                },
                "complaint_type": {
                    "type": "string",
                    "title": "Complaint type",
                    "step": "What happened",
                    "enum": [
                        "Unwanted calls or texts",
                        "Phone billing",
                        "Internet service",
                        "Television or radio",
                    ],
                },
                "description": {
                    "type": "string",
                    "title": "What happened?",
                    "format": "textarea",
                    "minLength": 20,
                    "maxLength": 4000,
                    "step": "What happened",
                },
            },
        },
    )

    def __init__(self) -> None:
        self.mode = os.getenv("FCC_CONNECTOR_MODE", "simulate").lower()
        self.endpoint = os.getenv("FCC_API_URL", "http://localhost:8001/fcc/robocall")

    async def submit(self, complaint: dict) -> dict:
        logger.info("fcc_submission_started", extra={"agency": self.agency_name})
        if self.mode == "simulate":
            reference = f"FCC-{secrets.token_hex(3).upper()}"
            return {"state": "submitted", "agency_reference": reference}

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(self.endpoint, json=complaint)
            response.raise_for_status()
        payload = response.json()
        return {
            "state": payload.get("state", "submitted"),
            "agency_reference": payload.get("reference"),
        }

    async def status(self, reference_id: str) -> dict:
        return {"state": "submitted", "agency_reference": reference_id}
