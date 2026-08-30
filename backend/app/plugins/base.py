# backend/app/plugins/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

DISCLAIMER = (
    "Citizen Karen is an independent service, not a government service or legal "
    "advice. Demo agency interactions are simulated unless explicitly identified."
)


@dataclass(frozen=True)
class PluginManifest:
    """Public, serializable contract consumed by the API and dynamic form UI."""

    key: str
    name: str
    short_name: str
    version: str
    description: str
    official_url: str
    category: str
    risk_score: int
    risk_level: str
    automation: str
    simulated: bool
    kyc_level: str
    restrictions: tuple[str, ...]
    form_schema: dict[str, Any]


class AgencyPlugin(ABC):
    manifest: PluginManifest

    def validate(self, complaint: dict[str, Any]) -> dict[str, Any]:
        """Plugin hook for agency-specific normalization and validation."""
        return complaint

    @abstractmethod
    async def submit(self, complaint: dict[str, Any]) -> dict[str, Any]:
        """
        Forward a complaint to an upstream agency.
        Return a dict e.g. {'state': 'submitted', 'agency_reference': 'ABC123'}.
        """

    @abstractmethod
    async def status(self, reference_id: str) -> dict[str, Any]:
        """
        Check status for an upstream complaint reference.
        """

    async def escalate(self, reference_id: str) -> dict[str, Any]:
        """Default escalation is manual review; plugins may override it."""
        return {
            "state": "needs_attention",
            "agency_reference": reference_id,
            "escalation": "manual_review",
        }
