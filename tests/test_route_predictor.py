"""Tests for Module 2 — Trafficking Route Predictor."""

import pytest

from backend.modules.route_predictor import (
    activate_corridor_alerts,
    get_known_destinations,
    get_known_sources,
    predict_routes,
)


class TestPredictRoutes:
    def test_known_source_returns_routes(self):
        routes = predict_routes("Murshidabad")
        assert len(routes) > 0
        destinations = {r.destination for r in routes}
        assert "Delhi" in destinations

    def test_unknown_source_returns_empty(self):
        routes = predict_routes("UnknownPlace")
        assert routes == []

    def test_route_has_checkpoints(self):
        routes = predict_routes("Murshidabad")
        for route in routes:
            assert len(route.checkpoints) > 0
            for cp in route.checkpoints:
                assert cp.location
                assert cp.estimated_arrival_hours >= 0

    def test_route_has_transport_modes(self):
        routes = predict_routes("Murshidabad")
        for route in routes:
            assert len(route.transport_modes) > 0

    def test_estimated_total_hours_positive(self):
        routes = predict_routes("Malda")
        for route in routes:
            assert route.estimated_total_hours is not None
            assert route.estimated_total_hours > 0


class TestCorridorActivation:
    def test_activate_known_source(self):
        activation = activate_corridor_alerts("Murshidabad")
        assert activation.source == "Murshidabad"
        assert len(activation.alerts) > 0
        assert len(activation.routes) > 0

    def test_activate_unknown_source(self):
        activation = activate_corridor_alerts("Narnia")
        assert activation.alerts == []
        assert activation.routes == []

    def test_no_duplicate_checkpoints(self):
        activation = activate_corridor_alerts("Murshidabad")
        locations = [a.checkpoint for a in activation.alerts]
        assert len(locations) == len(set(locations))


class TestSeedData:
    def test_known_sources_not_empty(self):
        assert len(get_known_sources()) > 0

    def test_known_destinations_not_empty(self):
        assert len(get_known_destinations()) > 0
