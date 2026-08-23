from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

BASE_MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "app" / "plugins" / "base.py"
)
BASE_SPEC = spec_from_file_location(
    "plugin_base",
    BASE_MODULE_PATH,
)
assert BASE_SPEC and BASE_SPEC.loader
BASE_MODULE = module_from_spec(BASE_SPEC)
BASE_SPEC.loader.exec_module(BASE_MODULE)
AgencyPlugin = BASE_MODULE.AgencyPlugin


class CompletePlugin(AgencyPlugin):
    async def submit(self, complaint: dict) -> dict:
        return {"state": "submitted", "agency_reference": "abc"}

    async def status(self, reference_id: str) -> dict:
        return {"state": "acknowledged", "agency_reference": reference_id}


class MissingStatusPlugin(AgencyPlugin):
    async def submit(self, complaint: dict) -> dict:
        return {"state": "submitted", "agency_reference": "abc"}


def test_agency_plugin_is_abstract():
    with pytest.raises(TypeError):
        AgencyPlugin()


def test_plugin_missing_required_method_is_abstract():
    with pytest.raises(TypeError):
        MissingStatusPlugin()


def test_plugin_with_submit_and_status_can_be_instantiated():
    plugin = CompletePlugin()
    assert isinstance(plugin, AgencyPlugin)
