# backend/app/plugins/base.py
from abc import ABC

class AgencyPlugin(ABC):
    def matches(self, data: dict) -> bool:
        """
        Return True if this plugin should handle the given complaint data.
        """
        return False

    def forward(self, data: dict) -> dict:
        """
        Forward the complaint to upstream agency.
        Return a dict e.g. {'success': True, 'agency_id': 'IRS', 'agency_response': {...}}
        Raise exceptions on failures.
        """
        raise NotImplementedError

    async def submit(self, complaint: dict) -> dict:
        """
        Submit a complaint payload to an upstream agency and return a normalized response.
        """
        raise NotImplementedError

    async def status(self, reference_id: str) -> dict:
        """
        Fetch status for a previously submitted agency reference.
        """
        raise NotImplementedError
