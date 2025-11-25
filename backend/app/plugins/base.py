from abc import ABC, abstractmethod
from typing import Dict, Any

class AgencyPlugin(ABC):
    agency_name: str

    @abstractmethod
    async def submit(self, complaint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit normalized complaint payload to upstream agency.
        Returns a dict with at least:
        - state: str
        - agency_reference: Optional[str]
        """
        ...

    @abstractmethod
    async def status(self, reference_id: str) -> Dict[str, Any]:
        """
        Get status from upstream agency by reference ID.
        """
        ...

