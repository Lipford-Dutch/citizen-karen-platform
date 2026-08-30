import hashlib
import secrets
from typing import Any

from .base import AgencyPlugin, PluginManifest


def _schema(
    title: str, topics: list[str], *, sensitive: bool = False
) -> dict[str, Any]:
    properties: dict[str, Any] = {
        "full_name": {
            "type": "string",
            "title": "Full name",
            "minLength": 2,
            "step": "About you",
        },
        "email": {
            "type": "string",
            "format": "email",
            "title": "Email",
            "step": "About you",
        },
        "complaint_type": {
            "type": "string",
            "title": "Issue type",
            "enum": topics,
            "step": "Your issue",
        },
        "description": {
            "type": "string",
            "title": "Describe what happened",
            "format": "textarea",
            "minLength": 20,
            "maxLength": 4000,
            "step": "Your issue",
        },
    }
    if sensitive:
        properties["identity_confirmation"] = {
            "type": "boolean",
            "title": "I understand this demo does not verify my government identity",
            "step": "Safety check",
        }
    return {
        "title": title,
        "type": "object",
        "required": ["full_name", "email", "complaint_type", "description"],
        "properties": properties,
    }


class MockAgencyPlugin(AgencyPlugin):
    prefix = "MOCK"

    async def submit(self, complaint: dict[str, Any]) -> dict[str, Any]:
        self.validate(complaint)
        return {
            "state": "submitted",
            "agency_reference": f"{self.prefix}-SIM-{secrets.token_hex(3).upper()}",
            "simulated": True,
        }

    async def status(self, reference_id: str) -> dict[str, Any]:
        return {
            "state": "under_review",
            "agency_reference": reference_id,
            "simulated": True,
        }


class IrsPlugin(MockAgencyPlugin):
    prefix = "IRS"
    manifest = PluginManifest(
        "irs",
        "Internal Revenue Service",
        "IRS",
        "1.0.0-demo",
        "Tax administration issue routing demonstration.",
        "https://www.irs.gov/help/let-us-help-you",
        "Government",
        88,
        "high",
        "High-fidelity mock only; restricted IRS portals are never automated.",
        True,
        "high",
        ("No IRS login", "No SSN collection", "Manual review required"),
        _schema(
            "IRS issue",
            ["Tax notice", "Refund delay", "Identity concern"],
            sensitive=True,
        ),
    )


class FtcPlugin(MockAgencyPlugin):
    prefix = "FTC"
    manifest = PluginManifest(
        "ftc",
        "Federal Trade Commission",
        "FTC",
        "1.0.0-demo",
        "Fraud, scam, identity-theft, and unfair-practice routing.",
        "https://reportfraud.ftc.gov/",
        "Consumer",
        62,
        "elevated",
        "High-fidelity mock; links to the official portal remain available.",
        True,
        "medium",
        ("No identity impersonation",),
        _schema(
            "FTC report",
            ["Scam or fraud", "Identity theft", "Unfair business practice"],
        ),
    )


class EpaPlugin(MockAgencyPlugin):
    prefix = "EPA"
    manifest = PluginManifest(
        "epa",
        "Environmental Protection Agency",
        "EPA",
        "1.0.0-demo",
        "Environmental concern and tip routing demonstration.",
        "https://www.epa.gov/tips",
        "Environment",
        48,
        "moderate",
        "High-fidelity mock only.",
        True,
        "low",
        ("Emergency reports must use local emergency services",),
        _schema(
            "EPA environmental concern",
            ["Air", "Water", "Waste or dumping", "Chemical release"],
        ),
    )


class CfpbPlugin(MockAgencyPlugin):
    prefix = "CFPB"
    manifest = PluginManifest(
        "cfpb",
        "Consumer Financial Protection Bureau",
        "CFPB",
        "1.0.0-demo",
        "Consumer-finance complaint routing demonstration.",
        "https://www.consumerfinance.gov/complaint/",
        "Consumer",
        71,
        "elevated",
        "High-fidelity mock only; no financial account credentials are accepted.",
        True,
        "medium",
        ("No account passwords", "No payment card numbers"),
        _schema(
            "CFPB complaint",
            ["Credit reporting", "Debt collection", "Mortgage", "Bank account"],
        ),
    )


class DmvPlugin(MockAgencyPlugin):
    prefix = "DMV"
    manifest = PluginManifest(
        "state-dmv",
        "Example State Department of Motor Vehicles",
        "State DMV",
        "1.0.0-demo",
        "Generic state motor-vehicle service example; not tied to a real state.",
        "https://www.usa.gov/state-motor-vehicle-services",
        "State",
        75,
        "elevated",
        "Synthetic state-agency mock only.",
        True,
        "high",
        ("No license number collection", "No authenticated portal access"),
        _schema(
            "State DMV issue",
            ["Registration", "Title", "License service", "Dealer complaint"],
            sensitive=True,
        ),
    )


class BenefitsPlugin(MockAgencyPlugin):
    prefix = "BEN"
    manifest = PluginManifest(
        "benefits",
        "Public Benefits Navigator Demo",
        "Benefits",
        "1.0.0-demo",
        "Generic benefits routing example with manual-review fallback.",
        "https://www.usa.gov/benefits",
        "Government",
        66,
        "elevated",
        "Synthetic mock only.",
        True,
        "medium",
        ("No eligibility determination", "No legal advice"),
        _schema(
            "Benefits issue",
            ["Application delay", "Incorrect notice", "Accessibility barrier"],
        ),
    )


class FailurePronePlugin(MockAgencyPlugin):
    prefix = "LAB"
    manifest = PluginManifest(
        "failure-lab",
        "Reliability Test Agency",
        "Failure Lab",
        "1.0.0-demo",
        "Synthetic connector for demonstrating retry, failure, and escalation paths.",
        "https://www.usa.gov/complaints",
        "Demo",
        95,
        "critical",
        "Synthetic deterministic failure simulator.",
        True,
        "low",
        ("Demo use only",),
        _schema(
            "Reliability test",
            ["Success path", "Retry path", "Permanent failure", "Escalation path"],
        ),
    )

    async def submit(self, complaint: dict[str, Any]) -> dict[str, Any]:
        issue = str(complaint.get("complaint_type", "")).lower()
        digest = hashlib.sha256(str(complaint).encode()).hexdigest()[:6].upper()
        if "permanent" in issue:
            raise ValueError("SIM_PERMANENT: deterministic demo rejection")
        if "retry" in issue:
            raise TimeoutError("SIM_RETRYABLE: deterministic upstream timeout")
        if "escalation" in issue:
            return {
                "state": "needs_attention",
                "agency_reference": f"LAB-SIM-{digest}",
                "simulated": True,
            }
        return {
            "state": "submitted",
            "agency_reference": f"LAB-SIM-{digest}",
            "simulated": True,
        }


MOCK_PLUGIN_TYPES: dict[str, type[AgencyPlugin]] = {
    plugin.manifest.key: plugin
    for plugin in (
        IrsPlugin,
        FtcPlugin,
        EpaPlugin,
        CfpbPlugin,
        DmvPlugin,
        BenefitsPlugin,
        FailurePronePlugin,
    )
}
