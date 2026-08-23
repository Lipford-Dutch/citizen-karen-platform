import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Dict

from .base import AgencyPlugin

_REGISTRY: Dict[str, AgencyPlugin] = {}


def _load_registry() -> None:
    if _REGISTRY:
        return

    package_name = __name__.rsplit(".", 1)[0]
    package_path = [str(Path(__file__).resolve().parent)]

    for module_info in pkgutil.iter_modules(package_path):
        module_name = module_info.name
        if module_name in {"base", "registry"}:
            continue
        if not module_name.endswith("_plugin"):
            continue

        module = importlib.import_module(f"{package_name}.{module_name}")
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module.__name__:
                continue
            agency_name = getattr(cls, "agency_name", None)
            if not agency_name:
                continue
            if not hasattr(cls, "submit"):
                continue

            key = str(agency_name).strip().lower()
            if key in _REGISTRY:
                raise ValueError(f"Duplicate plugin registration for agency: {key}")
            _REGISTRY[key] = cls()


def get_plugin(agency: str) -> AgencyPlugin:
    _load_registry()
    key = agency.strip().lower()
    if key not in _REGISTRY:
        raise ValueError(f"No plugin registered for agency: {agency}")
    return _REGISTRY[key]
