from .base import AgencyPlugin
from .fcc_plugin import FccPlugin
from .mock_agencies import MOCK_PLUGIN_TYPES

PLUGIN_TYPES: dict[str, type[AgencyPlugin]] = {
    "fcc": FccPlugin,
    **MOCK_PLUGIN_TYPES,
}


def get_plugin(agency: str) -> AgencyPlugin:
    key = agency.strip().lower()
    plugin_type = PLUGIN_TYPES.get(key)
    if plugin_type:
        return plugin_type()
    raise ValueError(
        f"Direct submission for '{agency}' is not available. Use its official portal."
    )


def list_plugins() -> list[AgencyPlugin]:
    return [plugin_type() for plugin_type in PLUGIN_TYPES.values()]
