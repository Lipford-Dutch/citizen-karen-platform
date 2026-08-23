# backend/app/plugins/sample_agency.py
import asyncio
import random

from .base import AgencyPlugin


class SampleAgencyPlugin(AgencyPlugin):
    async def submit(self, complaint: dict) -> dict:
        # Mock forwarding: simulate network call, random success/failure
        await asyncio.sleep(0.1)
        if random.random() < 0.9:
            return {
                "state": "submitted",
                "agency_reference": "SAMPLE_AGENCY",
            }
        raise RuntimeError("Upstream agency unavailable")

    async def status(self, reference_id: str) -> dict:
        return {
            "state": "acknowledged",
            "agency_reference": reference_id,
        }
