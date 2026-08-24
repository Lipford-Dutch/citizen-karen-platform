import os
import secrets

import httpx

from .base import AgencyPlugin
from ..logging_config import get_logger


logger = get_logger()


class FccPlugin(AgencyPlugin):
    agency_name = "fcc"

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
