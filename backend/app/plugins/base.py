# backend/app/plugins/base.py
from abc import ABC, abstractmethod

class AgencyPlugin(ABC):
    @abstractmethod
    def matches(self, data: dict) -> bool:
        """
        Return True if this plugin should handle the given complaint data.
        """
        pass

    @abstractmethod
    def forward(self, data: dict) -> dict:
        """
        Forward the complaint to upstream agency.
        Return a dict e.g. {'success': True, 'agency_id': 'IRS', 'agency_response': {...}}
        Raise exceptions on failures.
        """
        pass
