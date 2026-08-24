# backend/app/plugins/base.py
from abc import ABC, abstractmethod


class AgencyPlugin(ABC):
    @abstractmethod
    async def submit(self, complaint: dict) -> dict:
        """
        Forward a complaint to an upstream agency.
        Return a dict e.g. {'state': 'submitted', 'agency_reference': 'ABC123'}.
        """

    @abstractmethod
    async def status(self, reference_id: str) -> dict:
        """
        Check status for an upstream complaint reference.
        """
