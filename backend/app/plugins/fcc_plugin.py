import httpx
from .base import AgencyPlugin

class FccPlugin(AgencyPlugin):
    agency_name = "fcc"

    def matches(self, data: dict) -> bool:
        agency = (data.get("agency") or data.get("agency_hint") or "").lower()
        return agency == self.agency_name

    def forward(self, data: dict) -> dict:
        with httpx.Client() as client:
            resp = client.post(
                "http://mock-fcc:8001/fcc/robocall",
                json=data,
                timeout=10,
            )
        resp.raise_for_status()
        payload = resp.json()
        return {
            "success": payload.get("state", "submitted") in {"submitted", "accepted"},
            "agency_id": "FCC",
            "agency_response": payload,
        }

    async def submit(self, complaint):
        # In PoC, we call a mock FCC endpoint
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://mock-fcc:8001/fcc/robocall",
                json=complaint,
                timeout=10,
            )
        resp.raise_for_status()
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
