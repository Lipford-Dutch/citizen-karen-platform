import httpx
from .base import AgencyPlugin

class FccPlugin(AgencyPlugin):
    agency_name = "fcc"

    async def submit(self, complaint):
        # In PoC, we call a mock FCC endpoint
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://mock-fcc:8001/fcc/robocall",
                json=complaint,
                timeout=10,
            )
        data = resp.json()
        return {
            "state": data.get("state", "submitted"),
            "agency_reference": data.get("reference"),
        }

    async def status(self, reference_id: str):
        # For PoC, fake an 'acknowledged' state
        return {
            "state": "acknowledged",
            "agency_reference": reference_id,
        }

