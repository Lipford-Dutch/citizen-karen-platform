import re
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

CURRENT_CONSENT_VERSION = "2026-08-23"
SENSITIVE_PATTERNS = (
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
)


class ComplaintState(StrEnum):
    RECEIVED = "received"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    RETRYING = "retrying"
    NEEDS_ATTENTION = "needs_attention"
    ESCALATED = "escalated"
    DELETED = "deleted"


class ComplaintSubmission(BaseModel):
    agency: str = Field(default="fcc", pattern=r"^[a-z0-9_-]{2,40}$")
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone_number: str | None = Field(default=None, max_length=32)
    complaint_type: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=20, max_length=4000)
    consent: bool
    consent_version: str = Field(default=CURRENT_CONSENT_VERSION, max_length=32)
    website: str = Field(default="", max_length=0, exclude=True)
    dynamic_fields: dict[str, str | bool | int | float | None] = Field(
        default_factory=dict
    )

    @field_validator("full_name", "complaint_type", "description", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_privacy_and_consent(self) -> "ComplaintSubmission":
        if not self.consent:
            raise ValueError("Consent is required before a complaint can be submitted.")
        if self.consent_version != CURRENT_CONSENT_VERSION:
            raise ValueError(
                "The consent notice has changed. Review the current notice."
            )
        if any(pattern.search(self.description) for pattern in SENSITIVE_PATTERNS):
            raise ValueError(
                "Remove Social Security or payment card numbers before submitting."
            )
        return self


class ComplaintCreated(BaseModel):
    id: str
    tracking_id: str
    received: bool = True
    state: ComplaintState
    agency: str
    agency_reference: str | None = None
    submitted_at: str
    disclaimer: str = (
        "Citizen Karen is not a government service or legal advice. Demo agency "
        "interactions are simulated unless explicitly identified."
    )


class ComplaintStatus(BaseModel):
    id: str
    tracking_id: str
    state: ComplaintState
    agency: str
    agency_reference: str | None = None
    complaint_type: str
    submitted_at: str
    last_updated: str
    consent_version: str
    events: list[dict] = Field(default_factory=list)
    retry_count: int = 0
    next_action_at: str | None = None
    disclaimer: str = (
        "Citizen Karen is not a government service or legal advice. Demo agency "
        "interactions are simulated unless explicitly identified."
    )


class DeletionResponse(BaseModel):
    tracking_id: str
    state: ComplaintState = ComplaintState.DELETED
    message: str = "Citizen Karen's stored complaint copy has been deleted."
