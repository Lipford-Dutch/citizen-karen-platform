from datetime import UTC, datetime
from uuid import NAMESPACE_URL, uuid5

from .db import ComplaintStore
from .models import ComplaintSubmission

SEED_CASES = (
    ("CK-DEMO-FCC-001", "fcc", "Unwanted calls or texts", "under_review"),
    ("CK-DEMO-CFPB-002", "cfpb", "Credit reporting", "needs_attention"),
    ("CK-DEMO-EPA-003", "epa", "Water", "submitted"),
    ("CK-DEMO-IRS-004", "irs", "Tax notice", "under_review"),
    ("CK-DEMO-DMV-005", "state-dmv", "Registration", "resolved"),
    ("CK-DEMO-FTC-006", "ftc", "Scam or fraud", "resolved"),
    ("CK-DEMO-LAB-007", "failure-lab", "Retry path", "retrying"),
    ("CK-DEMO-BEN-008", "benefits", "Accessibility barrier", "escalated"),
)


def seed() -> int:
    store = ComplaintStore()
    store.init()
    created = 0
    for tracking_id, agency, complaint_type, state in SEED_CASES:
        if store.get(tracking_id):
            continue
        payload = ComplaintSubmission(
            agency=agency,
            full_name="Karen Citizen",
            email="karen@example.com",
            phone_number="+15555550100",
            complaint_type=complaint_type,
            description="Synthetic demo record created for a local stakeholder walkthrough only.",
            consent=True,
        )
        store.create(
            complaint_id=str(uuid5(NAMESPACE_URL, tracking_id)),
            tracking_id=tracking_id,
            submission=payload,
            owner_id="demo-citizen",
        )
        store.transition(
            tracking_id,
            state,
            event_type=f"demo_seed_{state}",
            agency_reference=f"{agency.upper()}-SIM-{tracking_id[-3:]}",
            metadata={
                "seeded": True,
                "simulated": True,
                "at": datetime.now(UTC).isoformat(),
            },
            increment_retry=state == "retrying",
        )
        created += 1
    store.engine.dispose()
    return created


if __name__ == "__main__":
    print(f"Seeded {seed()} demo cases")
