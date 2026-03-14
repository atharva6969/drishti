"""Tests for Module 6 — Privacy & Ethics Architecture."""

import pytest
from datetime import datetime, timedelta, timezone

from backend.models.schemas import CaseStatus, MissingPerson
from backend.modules.privacy import PrivacyManager


@pytest.fixture
def pm():
    return PrivacyManager()


@pytest.fixture
def person():
    return MissingPerson(
        name="Test Child",
        age=10,
        gender="female",
        last_seen_location="Murshidabad, West Bengal",
        reported_by="parent",
        consent_given=True,
    )


class TestConsentFirst:
    def test_register_with_consent(self, pm, person):
        assert pm.register_person(person) is True
        assert pm.is_registered(person.id)

    def test_register_without_consent(self, pm, person):
        person.consent_given = False
        assert pm.register_person(person) is False
        assert not pm.is_registered(person.id)


class TestCaseResolution:
    def test_resolve_registered_case(self, pm, person):
        pm.register_person(person)
        assert pm.resolve_case(person.id, "officer-1") is True

    def test_resolve_unknown_case(self, pm):
        assert pm.resolve_case("nonexistent", "officer-1") is False


class TestDataRetention:
    def test_purge_expired_records(self, pm):
        old_person = MissingPerson(
            name="Old Case",
            age=12,
            gender="male",
            last_seen_location="Malda",
            reported_by="ngo",
        )
        # Simulate an old resolved record
        old_person.created_at = datetime.now(timezone.utc) - timedelta(days=60)
        pm.register_person(old_person)
        pm.resolve_case(old_person.id, "officer-1")

        purged = pm.purge_expired()
        assert old_person.id in purged
        assert not pm.is_registered(old_person.id)

    def test_active_cases_not_purged(self, pm, person):
        pm.register_person(person)
        purged = pm.purge_expired()
        assert person.id not in purged
        assert pm.is_registered(person.id)


class TestAuditTrail:
    def test_audit_log_on_register(self, pm, person):
        pm.register_person(person)
        log = pm.get_audit_log(target_person_id=person.id)
        assert len(log) >= 1
        assert log[0].action == "person_registered"

    def test_public_log_action(self, pm):
        entry = pm.log_action("search_executed", "officer-5", "p-1", "face search")
        assert entry.action == "search_executed"
        assert entry.officer_id == "officer-5"

    def test_filter_audit_by_officer(self, pm):
        pm.log_action("action1", "officer-A")
        pm.log_action("action2", "officer-B")
        assert len(pm.get_audit_log(officer_id="officer-A")) == 1


class TestStateScopedAccess:
    def test_get_persons_for_state(self, pm, person):
        pm.register_person(person)
        wb = pm.get_persons_for_state("West Bengal")
        assert len(wb) == 1
        delhi = pm.get_persons_for_state("Delhi")
        assert len(delhi) == 0


class TestHumanInLoop:
    def test_always_requires_verification(self):
        assert PrivacyManager.requires_human_verification() is True
