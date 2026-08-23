import asyncio
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.plugins.fcc_plugin import FccPlugin
from app.plugins.registry import get_plugin


def test_fcc_plugin_matches():
    plugin = FccPlugin()
    assert plugin.matches({"agency": "fcc"})
    assert plugin.matches({"agency_hint": "FCC"})
    assert not plugin.matches({"agency": "ftc"})


def test_fcc_plugin_forward(monkeypatch):
    recorded = {}

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"state": "submitted", "reference": "FCC-123"}

    class DummyClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, json, timeout):
            recorded["url"] = url
            recorded["json"] = json
            recorded["timeout"] = timeout
            return DummyResponse()

    monkeypatch.setattr("app.plugins.fcc_plugin.httpx.Client", DummyClient)

    plugin = FccPlugin()
    result = plugin.forward({"agency": "fcc", "description": "robocall"})

    assert recorded["url"] == "http://mock-fcc:8001/fcc/robocall"
    assert recorded["json"]["description"] == "robocall"
    assert recorded["timeout"] == 10
    assert result["success"] is True
    assert result["agency_id"] == "FCC"
    assert result["agency_response"]["reference"] == "FCC-123"


def test_fcc_plugin_submit_and_registry(monkeypatch):
    recorded = {}

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"state": "accepted", "reference": "FCC-456"}

    class DummyAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json, timeout):
            recorded["url"] = url
            recorded["json"] = json
            recorded["timeout"] = timeout
            return DummyResponse()

    monkeypatch.setattr("app.plugins.fcc_plugin.httpx.AsyncClient", DummyAsyncClient)

    plugin = get_plugin("fcc")
    result = asyncio.run(plugin.submit({"agency": "fcc", "phoneNumber": "555-1212"}))

    assert isinstance(plugin, FccPlugin)
    assert recorded["url"] == "http://mock-fcc:8001/fcc/robocall"
    assert recorded["json"]["phoneNumber"] == "555-1212"
    assert result == {"state": "accepted", "agency_reference": "FCC-456"}
