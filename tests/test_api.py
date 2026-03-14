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
