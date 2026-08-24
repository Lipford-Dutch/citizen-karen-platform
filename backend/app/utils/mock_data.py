"""
mock_data.py — generate realistic fake complaint payloads for development and testing.

No third-party dependencies; uses only the Python standard library.
"""

import random
import uuid
import datetime

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

_FIRST_NAMES = [
    "Alice",
    "Bob",
    "Carol",
    "David",
    "Eve",
    "Frank",
    "Grace",
    "Hank",
    "Irene",
    "Jack",
    "Karen",
    "Leo",
    "Maria",
    "Nathan",
    "Olivia",
    "Paul",
    "Quinn",
    "Rachel",
    "Steve",
    "Tina",
    "Uma",
    "Victor",
    "Wendy",
    "Xena",
    "Yusuf",
    "Zoe",
]

_LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
    "Taylor",
    "Moore",
    "Jackson",
    "Martin",
    "Lee",
    "Perez",
    "Thompson",
    "White",
    "Harris",
    "Sanchez",
    "Clark",
    "Ramirez",
    "Lewis",
    "Robinson",
]

_EMAIL_DOMAINS = [
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "example.com",
    "test.org",
    "mail.net",
]

_AGENCIES = [
    "FCC",
    "EPA",
    "OSHA",
    "FTC",
    "HUD",
    "DOT",
    "FDA",
    "sample",
]

_COMPLAINT_TEMPLATES = [
    "I am filing a complaint regarding {topic}. The issue has been ongoing for {duration} "
    "and I have not received any resolution despite multiple attempts to resolve it.",
    "This complaint concerns {topic}. I believe this is a violation of consumer protection laws "
    "and requires immediate investigation.",
    "I would like to report {topic}. The responsible party has failed to address my concerns "
    "after {duration}.",
    "Filing a formal complaint about {topic}. I have documentation available upon request.",
    "I am writing to report an ongoing issue with {topic} that has caused me significant harm.",
]

_TOPICS = [
    "unauthorized billing charges",
    "deceptive advertising practices",
    "failure to provide contracted services",
    "data privacy violations",
    "harassment by a collections agency",
    "unsafe working conditions",
    "product safety defects",
    "unlicensed contracting work",
    "discriminatory rental practices",
    "interference with broadcast signals",
    "improper food handling at a local establishment",
    "excessive noise violations",
    "fraudulent warranty claims",
    "unsafe vehicle modifications",
    "prescription medication errors",
]

_DURATIONS = [
    "two weeks",
    "a month",
    "three months",
    "six months",
    "over a year",
    "several days",
    "more than 90 days",
]


# ---------------------------------------------------------------------------
# Generator functions
# ---------------------------------------------------------------------------


def _random_name() -> str:
    return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"


def _random_email(name: str) -> str:
    local = name.lower().replace(" ", ".")
    suffix = random.randint(1, 999)
    domain = random.choice(_EMAIL_DOMAINS)
    return f"{local}{suffix}@{domain}"


def _random_description() -> str:
    template = random.choice(_COMPLAINT_TEMPLATES)
    topic = random.choice(_TOPICS)
    duration = random.choice(_DURATIONS)
    return template.format(topic=topic, duration=duration)


def _random_timestamp(
    start: datetime.datetime | None = None,
    end: datetime.datetime | None = None,
) -> str:
    """Return a random ISO-8601 UTC timestamp between *start* and *end*."""
    if end is None:
        end = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    if start is None:
        start = end - datetime.timedelta(days=365)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    ts = start + datetime.timedelta(seconds=random_seconds)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_complaint(agency: str | None = None) -> dict:
    """Return a single mock complaint payload compatible with ComplaintIn.

    Args:
        agency: Agency hint to use. If *None*, a random one is chosen.

    Returns:
        A dict with keys: name, email, description, agency_hint, timestamp, tracking_id.
    """
    name = _random_name()
    return {
        "tracking_id": str(uuid.uuid4()),
        "name": name,
        "email": _random_email(name),
        "description": _random_description(),
        "agency_hint": agency if agency is not None else random.choice(_AGENCIES),
        "timestamp": _random_timestamp(),
    }


def generate_complaints(count: int = 10, agency: str | None = None) -> list[dict]:
    """Return a list of *count* mock complaint payloads.

    Args:
        count: Number of complaints to generate (default 10).
        agency: Optional fixed agency hint; if *None*, each complaint gets a random one.

    Returns:
        List of complaint dicts.
    """
    return [generate_complaint(agency=agency) for _ in range(count)]
