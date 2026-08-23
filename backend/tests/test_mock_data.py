"""tests/test_mock_data.py — unit tests for the mock data generation utility."""

import pytest
from app.utils.mock_data import generate_complaint, generate_complaints


class TestGenerateComplaint:
    def test_returns_dict(self):
        result = generate_complaint()
        assert isinstance(result, dict)

    def test_required_keys_present(self):
        result = generate_complaint()
        for key in ("tracking_id", "name", "email", "description", "agency_hint", "timestamp"):
            assert key in result, f"Missing key: {key}"

    def test_tracking_id_is_uuid(self):
        import uuid
        result = generate_complaint()
        # Should not raise
        uuid.UUID(result["tracking_id"])

    def test_email_contains_at(self):
        result = generate_complaint()
        assert "@" in result["email"]

    def test_timestamp_format(self):
        import re
        result = generate_complaint()
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", result["timestamp"])

    def test_agency_hint_fixed(self):
        result = generate_complaint(agency="FCC")
        assert result["agency_hint"] == "FCC"

    def test_agency_hint_random_when_not_specified(self):
        from app.utils.mock_data import _AGENCIES
        result = generate_complaint()
        assert result["agency_hint"] in _AGENCIES

    def test_description_is_non_empty_string(self):
        result = generate_complaint()
        assert isinstance(result["description"], str)
        assert len(result["description"]) > 10


class TestGenerateComplaints:
    def test_default_count(self):
        results = generate_complaints()
        assert len(results) == 10

    def test_custom_count(self):
        results = generate_complaints(count=5)
        assert len(results) == 5

    def test_all_items_are_dicts(self):
        results = generate_complaints(count=3)
        assert all(isinstance(r, dict) for r in results)

    def test_tracking_ids_are_unique(self):
        results = generate_complaints(count=50)
        ids = [r["tracking_id"] for r in results]
        assert len(set(ids)) == 50

    def test_fixed_agency_applied_to_all(self):
        results = generate_complaints(count=10, agency="EPA")
        assert all(r["agency_hint"] == "EPA" for r in results)
