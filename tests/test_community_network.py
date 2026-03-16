"""Tests for Module 3 — Community Intelligence Network."""

import pytest

from backend.models.schemas import MissingPerson, Sighting
from backend.modules.community_network import CommunityNetwork, CommunityReporter


@pytest.fixture
def network():
    net = CommunityNetwork()
    net.register_reporter(CommunityReporter("+91-1111", "Alice", 22.5, 88.3))
    net.register_reporter(CommunityReporter("+91-2222", "Bob", 22.51, 88.31))
    net.register_reporter(CommunityReporter("+91-3333", "Eve", 30.0, 78.0))  # far away
    return net


@pytest.fixture
def missing_person():
    return MissingPerson(
        name="Test Child",
        age=10,
        gender="female",
        last_seen_location="Murshidabad",
        reported_by="parent",
    )


class TestReporterRadius:
    def test_nearby_reporters_found(self, network):
        nearby = network.get_reporters_in_radius(22.5, 88.3, radius_km=50)
        phones = {r.phone for r in nearby}
        assert "+91-1111" in phones
        assert "+91-2222" in phones

    def test_far_reporter_excluded(self, network):
        nearby = network.get_reporters_in_radius(22.5, 88.3, radius_km=50)
        phones = {r.phone for r in nearby}
        assert "+91-3333" not in phones


class TestAlertDispatch:
    def test_dispatch_returns_records(self, network, missing_person):
        dispatches = network.dispatch_alert(missing_person, 22.5, 88.3)
        assert len(dispatches) == 2  # Alice + Bob
        assert all("DRISHTI ALERT" in d["message"] for d in dispatches)

    def test_dispatched_alerts_stored(self, network, missing_person):
        network.dispatch_alert(missing_person, 22.5, 88.3)
        assert len(network.dispatched_alerts) == 2


class TestSightings:
    def test_submit_and_retrieve(self, network):
        sighting = Sighting(
            missing_person_id="mp-1",
            reporter_phone="+91-9999",
            location="Howrah Station",
        )
        network.submit_sighting(sighting)
        results = network.get_sightings("mp-1")
        assert len(results) == 1
        assert results[0].location == "Howrah Station"

    def test_filter_by_person_id(self, network):
        network.submit_sighting(Sighting(missing_person_id="mp-1", reporter_phone="+91-1", location="A"))
        network.submit_sighting(Sighting(missing_person_id="mp-2", reporter_phone="+91-2", location="B"))
        assert len(network.get_sightings("mp-1")) == 1
        assert len(network.get_sightings()) == 2
