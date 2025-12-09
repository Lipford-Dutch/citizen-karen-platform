# Agency Plugin Integration Guide — Citizen Karen

This document describes how to integrate a new upstream agency (federal, state, regulatory) into Citizen Karen via the modular Plugin Framework.

---

## 🧩 Plugin Lifecycle & Module Structure

### Directory Layout (suggested)

backend/
plugins/
<agency_name>/
validators.py # payload validation & sanitization
schema.json # agency-specific data schema (JSON Schema / Pydantic schema)
submitter.py # logic to submit complaint/request to agency
status_checker.py # logic to check submission status / poll / retrieve updates
escalator.py # optional logic to escalate or submit follow-up / appeal
attachments/ # if agency requires document uploads: define attachment schema
config.template.env # template for required environment variables (API keys, credentials)
README.md # instructions, quirks, agency-specific notes


### Required Module Interface

Each agency module must expose:

```python
class AgencyModule:
    agency_id: str  # unique short identifier (e.g. "IRS", "FCC")
    
    def validate(payload: dict) -> dict:
        """Validate & sanitize citizen‑friendly data → returns cleaned data or raise ValidationError."""
    
    def submit(validated_data: dict) -> dict:
        """
        Submit to agency (API, form-filling, automation).
        Returns dict:
        {
          "success": bool,
          "agency_ticket": optional[str],
          "metadata": optional[dict]
        }
        Raise exception on irrecoverable error (to trigger retry/backoff).
        """
    
    def check_status(agency_ticket: str) -> dict:
        """
        Query agency for status of submission.
        Returns dict:
        {
          "status": str,              # e.g. "pending", "accepted", "rejected", etc.
          "agency_response": dict     # optional raw data from agency
        }
        """
    
    def escalate(agency_ticket: str, escalation_params: dict) -> dict:
        """
        Optional. For agencies supporting appeals, follow-up, or document submission.
        Returns similar dict as submit(). 
        """
