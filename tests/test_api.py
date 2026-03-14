"""Tests for the FastAPI application endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestHealthCheck:
    def test_health_returns_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["system"] == "DRISHTI"


class TestMissingPersonsAPI:
    def _make_person(self, **kwargs) -> dict:
        payload = {
            "name": "Priya Sharma",
            "age": 14,
            "gender": "female",
            "last_seen_location": "Howrah Station, West Bengal",
            "reported_by": "officer_001",
            "consent_given": True,
        }
        payload.update(kwargs)
        return payload

    def test_register_missing_person_success(self):
        resp = client.post("/api/v1/persons/", json=self._make_person())
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["status"] == "registered"

    def test_register_missing_person_no_consent(self):
        resp = client.post("/api/v1/persons/", json=self._make_person(consent_given=False))
        assert resp.status_code == 403
        assert "Consent" in resp.json()["detail"]

    def test_get_registered_person(self):
        # Register first, then retrieve
        reg = client.post("/api/v1/persons/", json=self._make_person())
        assert reg.status_code == 201
        person_id = reg.json()["id"]

        resp = client.get(f"/api/v1/persons/{person_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == person_id
        assert data["registered"] is True

    def test_get_nonexistent_person_returns_404(self):
        resp = client.get("/api/v1/persons/nonexistent-id-00000")
        assert resp.status_code == 404

    def test_resolve_case(self):
        reg = client.post("/api/v1/persons/", json=self._make_person())
        assert reg.status_code == 201
        person_id = reg.json()["id"]

        resp = client.post(f"/api/v1/persons/{person_id}/resolve?officer_id=officer_99")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == person_id
        assert data["status"] == "resolved"

    def test_resolve_nonexistent_case_returns_404(self):
        resp = client.post("/api/v1/persons/unknown-id/resolve?officer_id=officer_01")
        assert resp.status_code == 404


class TestAlertsAPI:
    def _register_hub(self, hub_id: str = "HUB_TEST_01") -> dict:
        resp = client.post(
            "/api/v1/alerts/hub",
            params={
                "hub_id": hub_id,
                "name": "Howrah Railway Station",
                "hub_type": "railway_station",
                "state": "West Bengal",
                "latitude": 22.5839,
                "longitude": 88.3424,
                "camera_count": 48,
            },
        )
        assert resp.status_code == 201
        return resp.json()

    def test_register_hub(self):
        data = self._register_hub("HUB_REG_01")
        assert data["hub_id"] == "HUB_REG_01"
        assert data["status"] == "registered"

    def test_list_hubs_returns_registered_hub(self):
        self._register_hub("HUB_LIST_01")
        resp = client.get("/api/v1/alerts/hub")
        assert resp.status_code == 200
        hub_ids = [h["hub_id"] for h in resp.json()]
        assert "HUB_LIST_01" in hub_ids

    def test_list_hubs_filter_by_type(self):
        self._register_hub("HUB_FILTER_01")
        resp = client.get("/api/v1/alerts/hub?hub_type=railway_station")
        assert resp.status_code == 200
        for h in resp.json():
            assert h["type"] == "railway_station"

    def test_trigger_hub_alert(self):
        self._register_hub("HUB_ALERT_01")
        resp = client.post(
            "/api/v1/alerts/hub/HUB_ALERT_01/alert",
            params={"missing_person_id": "person_xyz", "confidence": 0.92},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["hub_id"] == "HUB_ALERT_01"
        assert len(data["steps_completed"]) > 0

    def test_trigger_alert_unknown_hub_returns_404(self):
        resp = client.post(
            "/api/v1/alerts/hub/NONEXISTENT_HUB/alert",
            params={"missing_person_id": "person_abc", "confidence": 0.80},
        )
        assert resp.status_code == 404


class TestRoutesAPI:
    def test_list_sources(self):
        resp = client.get("/api/v1/routes/sources")
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    def test_list_destinations(self):
        resp = client.get("/api/v1/routes/destinations")
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    def test_predict_known_source(self):
        resp = client.get("/api/v1/routes/predict/Murshidabad")
        assert resp.status_code == 200
        routes = resp.json()
        assert len(routes) > 0

    def test_predict_unknown_source(self):
        resp = client.get("/api/v1/routes/predict/Narnia")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_activate_corridor(self):
        resp = client.post("/api/v1/routes/activate/Murshidabad")
        assert resp.status_code == 200
        data = resp.json()
        assert data["source"] == "Murshidabad"
        assert data["alerts_count"] > 0


class TestSightingsAPI:
    def test_submit_sighting(self):
        resp = client.post(
            "/api/v1/sightings/",
            json={
                "reporter_phone": "+91-9999",
                "location": "Howrah Station",
                "description": "Saw a child matching description",
            },
        )
        assert resp.status_code == 201
        assert "id" in resp.json()
