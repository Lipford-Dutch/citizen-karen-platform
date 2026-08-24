import sys
from pathlib import Path
from typing import Any

import anyio
import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import main
from app.db import ComplaintStore


class AppClient:
    """Small synchronous facade over httpx's native ASGI transport."""

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        async def send() -> httpx.Response:
            transport = httpx.ASGITransport(app=main.app)
            async with httpx.AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as client:
                return await client.request(method, url, **kwargs)

        return anyio.run(send)

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("DELETE", url, **kwargs)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "store", ComplaintStore(tmp_path / "test.db"))
    monkeypatch.setenv("FCC_CONNECTOR_MODE", "simulate")
    main.store.init()
    yield AppClient()


@pytest.fixture
def complaint_payload():
    return {
        "agency": "fcc",
        "full_name": "Alex Citizen",
        "email": "alex@example.com",
        "phone_number": "+15555551234",
        "complaint_type": "Unwanted calls or texts",
        "description": "I received repeated automated calls after asking the caller to stop.",
        "consent": True,
        "consent_version": "2026-08-23",
    }
