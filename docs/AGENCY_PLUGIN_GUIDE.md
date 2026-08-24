# Agency Plugin Developer Guide — Citizen Karen

This document describes how to build and register a new agency plugin so that citizen complaints can be automatically routed to federal, state, or regulatory bodies via the Citizen Karen plugin framework.

---

## Overview

The plugin framework lives in `backend/app/plugins/`. Every agency integration is a Python class that inherits from `AgencyPlugin` (defined in `backend/app/plugins/base.py`). The complaint router in `backend/app/complaints.py` iterates over all registered plugin instances, calls `matches()` on each one, and invokes `forward()` on the first match.

---

## The `AgencyPlugin` Base Class

```python
# backend/app/plugins/base.py
from abc import ABC, abstractmethod

class AgencyPlugin(ABC):
    @abstractmethod
    def matches(self, data: dict) -> bool:
        """
        Return True if this plugin should handle the given complaint data.
        Inspect any field in `data` (e.g. agency_hint, category, zip_code).
        """

    @abstractmethod
    def forward(self, data: dict) -> dict:
        """
        Forward the complaint to the upstream agency.

        Return a dict with at least:
          {
            "success": bool,
            "agency_id": str,          # short agency identifier, e.g. "FCC"
            "agency_response": dict    # raw response from the agency
          }

        Raise an exception on irrecoverable errors — the router will catch it,
        log it, and leave the complaint in "pending" state for retry.
        """
```

---

## Step-by-Step: Building a New Plugin

### 1. Create a new file in `backend/app/plugins/`

Name it after the agency, e.g. `epa_plugin.py`.

```python
# backend/app/plugins/epa_plugin.py
import httpx
from .base import AgencyPlugin

EPA_ENDPOINT = "https://echo.epa.gov/api/submissions"  # example

class EpaPlugin(AgencyPlugin):
    agency_name = "epa"

    def matches(self, data: dict) -> bool:
        # Route complaints that explicitly target the EPA,
        # or complaints about environmental issues.
        return (
            data.get("agency_hint", "").lower() == "epa"
            or data.get("category", "").lower() == "environmental"
        )

    def forward(self, data: dict) -> dict:
        payload = {
            "description": data.get("description"),
            "reporter_email": data.get("email"),
        }
        resp = httpx.post(EPA_ENDPOINT, json=payload, timeout=15)
        resp.raise_for_status()          # propagate HTTP errors as exceptions
        body = resp.json()
        return {
            "success": True,
            "agency_id": "EPA",
            "agency_response": body,
        }
```

Key rules:
- `matches()` must be **fast and side-effect-free** — it is called for every complaint.
- `forward()` should **raise** on failure so the router can catch, log, and retry.
- Use environment variables (via `os.getenv`) for API keys and endpoint URLs; never hardcode secrets.

### 2. Register the plugin in `backend/app/plugins/registry.py`

```python
# backend/app/plugins/registry.py
from typing import Dict
from .base import AgencyPlugin
from .fcc_plugin import FccPlugin
from .epa_plugin import EpaPlugin   # <-- import your new plugin

_REGISTRY: Dict[str, AgencyPlugin] = {
    "fcc": FccPlugin(),
    "epa": EpaPlugin(),             # <-- add an entry
}

def get_plugin(agency: str) -> AgencyPlugin:
    key = agency.lower()
    if key not in _REGISTRY:
        raise ValueError(f"No plugin registered for agency: {agency}")
    return _REGISTRY[key]
```

### 3. (Optional) Add the plugin instance to the complaint router

If your plugin should participate in the **automatic routing** loop (complaint submitted → plugin iterates), add it to `PLUGIN_INSTANCES` in `backend/app/complaints.py`:

```python
# backend/app/complaints.py  (excerpt)
from ..plugins import sample_agency, epa_plugin   # add your module

PLUGIN_INSTANCES = [
    sample_agency.SampleAgencyPlugin(),
    epa_plugin.EpaPlugin(),          # <-- added
]
```

The router already handles the iteration, error catching, and status updates — you don't need to modify any other file.

---

## Existing Plugins (reference implementations)

| Plugin file | Agency | `matches()` logic | Notes |
|---|---|---|---|
| `fcc_plugin.py` | FCC | (routed via registry key `"fcc"`) | Uses async `httpx`; calls mock-fcc service in PoC |
| `sample_agency.py` | SAMPLE_AGENCY | `agency_hint == "sample"` | Synchronous; simulates random upstream failures |

---

## Checklist for a New Plugin

- [ ] Class inherits from `AgencyPlugin` in `backend/app/plugins/base.py`
- [ ] `matches(self, data)` implemented — returns `bool`
- [ ] `forward(self, data)` implemented — returns `{"success": bool, "agency_id": str, "agency_response": dict}`
- [ ] Sensitive config (API keys, URLs) read from environment variables
- [ ] Plugin registered in `registry.py` and/or added to `PLUGIN_INSTANCES` in `complaints.py`
- [ ] Unit test added under `backend/tests/` (see `test_plugin_registry.py` for patterns)

---

## Testing Your Plugin

Run the backend test suite from the `backend/` directory:

```bash
cd backend
pytest --cov=./ --cov-report=xml
```

To test the plugin in isolation, create a test file following the pattern in `backend/tests/test_plugin_registry.py`. A minimal test looks like:

```python
from app.plugins.epa_plugin import EpaPlugin

def test_epa_matches():
    plugin = EpaPlugin()
    assert plugin.matches({"agency_hint": "epa"})
    assert plugin.matches({"category": "environmental"})
    assert not plugin.matches({"agency_hint": "fcc"})

def test_epa_forward(respx_mock):
    import respx, httpx
    respx_mock.post("https://echo.epa.gov/api/submissions").mock(
        return_value=httpx.Response(200, json={"id": "EPA-001"})
    )
    plugin = EpaPlugin()
    result = plugin.forward({"description": "dumping", "email": "test@example.com"})
    assert result["success"] is True
    assert result["agency_id"] == "EPA"
