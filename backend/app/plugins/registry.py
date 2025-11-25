from typing import Dict
from .base import AgencyPlugin
from .fcc_plugin import FccPlugin

# Simple registry for now; later can be dynamic loading
_REGISTRY: Dict[str, AgencyPlugin] = {
    "fcc": FccPlugin(),
    # "irs": IrsPlugin(), etc...
}

def get_plugin(agency: str) -> AgencyPlugin:
    key = agency.lower()
    if key not in _REGISTRY:
        raise ValueError(f"No plugin registered for agency: {agency}")
    return _REGISTRY[key]

