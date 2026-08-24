from .base import AgencyPlugin
from .fcc_plugin import FccPlugin


def get_plugin(agency: str) -> AgencyPlugin:
    key = agency.strip().lower()
    if key == "fcc":
        return FccPlugin()
    raise ValueError(
        f"Direct submission for '{agency}' is not available. Use its official portal."
    )
