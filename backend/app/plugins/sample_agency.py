# backend/app/plugins/sample_agency.py
import random
import time

from .base import AgencyPlugin


class SampleAgencyPlugin(AgencyPlugin):
    def matches(self, data: dict) -> bool:
        # Simple example: if complaint has type "sample", handle it
        return data.get("agency_hint") == "sample"

    def forward(self, data: dict) -> dict:
        # Mock forwarding: simulate network call, random success/failure
        time.sleep(0.1)
        if random.random() < 0.9:
            return {
                "success": True,
                "agency_id": "SAMPLE_AGENCY",
                "agency_response": {"message": "Accepted"},
            }
        else:
            raise RuntimeError("Upstream agency unavailable")
