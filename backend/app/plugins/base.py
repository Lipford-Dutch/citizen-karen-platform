# backend/app/plugins/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict


class AgencyPlugin(ABC):
    @abstractmethod
    async def submit(self, complaint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit complaint data to the upstream agency.
        """
        pass

    @abstractmethod
    async def status(self, reference_id: str) -> Dict[str, Any]:
        """
        Query status for a previously submitted complaint reference.
        """
        pass
