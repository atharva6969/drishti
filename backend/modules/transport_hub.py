"""Module 5 — Transport Hub Integration.

Manages the registry of integrated transport hubs (railway stations,
bus terminals, airports, border checkposts) and the alert protocol
when a potential match is detected at a hub.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class HubType(str, Enum):
    RAILWAY_STATION = "railway_station"
    BUS_TERMINAL = "bus_terminal"
    AIRPORT = "airport"
    BORDER_CHECKPOST = "border_checkpost"


class AlertProtocolStep(str, Enum):
    CONTROL_ROOM_ALERT = "control_room_alert"
    RPF_NOTIFICATION = "rpf_notification"
    AHTU_CALL = "ahtu_call"
    FAMILY_NOTIFICATION = "family_notification"


@dataclass
class TransportHub:
    """A registered transport hub with camera integration."""

    hub_id: str
    name: str
    hub_type: HubType
    state: str
    latitude: float
    longitude: float
    camera_count: int = 0
    active: bool = True


@dataclass
class HubAlertRecord:
    """Record of an alert dispatched at a transport hub."""

    hub_id: str
    missing_person_id: str
    confidence: float
    steps_completed: list[AlertProtocolStep] = field(default_factory=list)
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    verified: bool = False


class TransportHubRegistry:
    """Registry and alert protocol for transport hubs."""

    def __init__(self) -> None:
        self._hubs: dict[str, TransportHub] = {}
        self._alert_records: list[HubAlertRecord] = []

    # ── Hub management ────────────────────────────────────────────

    def register_hub(self, hub: TransportHub) -> None:
        self._hubs[hub.hub_id] = hub

    def get_hub(self, hub_id: str) -> Optional[TransportHub]:
        return self._hubs.get(hub_id)

    def list_hubs(
        self,
        hub_type: Optional[HubType] = None,
        state: Optional[str] = None,
    ) -> list[TransportHub]:
        hubs = list(self._hubs.values())
        if hub_type:
            hubs = [h for h in hubs if h.hub_type == hub_type]
        if state:
            hubs = [h for h in hubs if h.state == state]
        return hubs

    # ── Alert protocol ────────────────────────────────────────────

    def execute_alert_protocol(
        self,
        hub_id: str,
        missing_person_id: str,
        confidence: float,
    ) -> Optional[HubAlertRecord]:
        """Execute the full 4-step alert protocol at a hub.

        Steps:
        1. Station Control Room receives on-screen alert.
        2. Nearest RPF officer gets push notification with photo.
        3. AHTU duty officer receives automated call.
        4. Family receives "possible sighting" notification.

        In production each step calls the relevant notification service.
        This method records the steps synchronously for the MVP.
        """
        hub = self.get_hub(hub_id)
        if hub is None or not hub.active:
            return None

        steps = [
            AlertProtocolStep.CONTROL_ROOM_ALERT,
            AlertProtocolStep.RPF_NOTIFICATION,
            AlertProtocolStep.AHTU_CALL,
            AlertProtocolStep.FAMILY_NOTIFICATION,
        ]

        record = HubAlertRecord(
            hub_id=hub_id,
            missing_person_id=missing_person_id,
            confidence=confidence,
            steps_completed=steps,
        )
        self._alert_records.append(record)
        return record

    def get_alert_records(
        self,
        hub_id: Optional[str] = None,
        missing_person_id: Optional[str] = None,
    ) -> list[HubAlertRecord]:
        records = self._alert_records
        if hub_id:
            records = [r for r in records if r.hub_id == hub_id]
        if missing_person_id:
            records = [r for r in records if r.missing_person_id == missing_person_id]
        return records
