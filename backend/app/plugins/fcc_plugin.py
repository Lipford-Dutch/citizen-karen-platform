import httpx
from .base import AgencyPlugin
from ..logging_config import get_logger

logger = get_logger()


class FccPlugin(AgencyPlugin):
    agency_name = "fcc"

    async def submit(self, complaint):
        logger.info("fcc_plugin_submit_started", extra={"agency": self.agency_name})
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "http://mock-fcc:8001/fcc/robocall",
                    json=complaint,
                    timeout=10,
                )
            data = resp.json()
            logger.info(
                "fcc_plugin_submit_succeeded",
                extra={"agency": self.agency_name, "state": data.get("state")},
            )
            return {
                "state": data.get("state", "submitted"),
                "agency_reference": data.get("reference"),
            }
        except Exception as exc:
            logger.error(
                "fcc_plugin_submit_error",
                extra={"agency": self.agency_name, "error": str(exc)},
            )
            raise

    async def status(self, reference_id: str):
        logger.info(
            "fcc_plugin_status_checked",
            extra={"agency": self.agency_name, "reference_id": reference_id},
        )
        return {
            "state": "acknowledged",
            "agency_reference": reference_id,
        }

