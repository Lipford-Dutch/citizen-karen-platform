from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, model_validator


class ComplaintSubmission(BaseModel):
    agency: Optional[str] = None
    agency_hint: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    description: str
    timestamp: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        data = dict(values)
        if "phoneNumber" in data and "phone_number" not in data:
            data["phone_number"] = data["phoneNumber"]
        if "agencyHint" in data and "agency_hint" not in data:
            data["agency_hint"] = data["agencyHint"]
        if "agency_hint" in data and "agency" not in data:
            data["agency"] = data["agency_hint"]
        if data.get("timestamp") in (None, ""):
            data["timestamp"] = datetime.now(timezone.utc)
        return data

    @model_validator(mode="after")
    def require_agency(self) -> "ComplaintSubmission":
        if not self.agency:
            raise ValueError("agency (or agency_hint) is required")
        return self


class NormalizedComplaint(BaseModel):
    agency: str
    description: str
    timestamp: datetime
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None

    @classmethod
    def from_submission(cls, payload: ComplaintSubmission) -> "NormalizedComplaint":
        return cls(
            agency=payload.agency,
            description=payload.description,
            timestamp=payload.timestamp,
            name=payload.name,
            email=payload.email,
            phone_number=payload.phone_number,
        )

    def to_plugin_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "agency": self.agency,
            "agency_hint": self.agency,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.name:
            payload["name"] = self.name
        if self.email:
            payload["email"] = self.email
        if self.phone_number:
            payload["phone_number"] = self.phone_number
            payload["phoneNumber"] = self.phone_number
        return payload
