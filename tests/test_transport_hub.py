"""Tests for Module 5 — Transport Hub Integration."""

import pytest

from backend.modules.transport_hub import (
    AlertProtocolStep,
    HubType,
    TransportHub,
    TransportHubRegistry,
)


@pytest.fixture
def registry():
    reg = TransportHubRegistry()
    reg.register_hub(
        TransportHub(
            hub_id="HWH",
            name="Howrah Junction",
            hub_type=HubType.RAILWAY_STATION,
            state="West Bengal",
            latitude=22.58,
            longitude=88.34,
            camera_count=120,
        )
    )
    reg.register_hub(
        TransportHub(
            hub_id="NDLS",
            name="New Delhi",
            hub_type=HubType.RAILWAY_STATION,
            state="Delhi",
            latitude=28.64,
            longitude=77.22,
            camera_count=200,
        )
    )
    return reg


class TestHubManagement:
    def test_register_and_retrieve(self, registry):
        hub = registry.get_hub("HWH")
        assert hub is not None
        assert hub.name == "Howrah Junction"

    def test_list_by_type(self, registry):
        hubs = registry.list_hubs(hub_type=HubType.RAILWAY_STATION)
        assert len(hubs) == 2

    def test_list_by_state(self, registry):
        hubs = registry.list_hubs(state="Delhi")
        assert len(hubs) == 1
        assert hubs[0].hub_id == "NDLS"

    def test_get_unknown_hub(self, registry):
        assert registry.get_hub("UNKNOWN") is None


class TestAlertProtocol:
    def test_full_protocol_executed(self, registry):
        record = registry.execute_alert_protocol("HWH", "mp-1", confidence=0.92)
        assert record is not None
        assert len(record.steps_completed) == 4
        assert AlertProtocolStep.CONTROL_ROOM_ALERT in record.steps_completed
        assert AlertProtocolStep.RPF_NOTIFICATION in record.steps_completed
        assert AlertProtocolStep.AHTU_CALL in record.steps_completed
        assert AlertProtocolStep.FAMILY_NOTIFICATION in record.steps_completed

    def test_alert_on_inactive_hub(self, registry):
        hub = registry.get_hub("HWH")
        hub.active = False
        record = registry.execute_alert_protocol("HWH", "mp-1", 0.9)
        assert record is None

    def test_alert_on_unknown_hub(self, registry):
        record = registry.execute_alert_protocol("FAKE", "mp-1", 0.9)
        assert record is None

    def test_alert_records_stored(self, registry):
        registry.execute_alert_protocol("HWH", "mp-1", 0.92)
        records = registry.get_alert_records(hub_id="HWH")
        assert len(records) == 1

    def test_filter_records_by_person(self, registry):
        registry.execute_alert_protocol("HWH", "mp-1", 0.92)
        registry.execute_alert_protocol("NDLS", "mp-2", 0.88)
        assert len(registry.get_alert_records(missing_person_id="mp-1")) == 1
