import pytest
import networkx as nx
from app.modules.route_predictor import RoutePredictor


@pytest.fixture
def predictor():
    return RoutePredictor()


def test_route_graph_building(predictor):
    graph = predictor.route_graph
    
    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0


def test_route_graph_has_known_nodes(predictor):
    nodes = list(predictor.route_graph.nodes())
    
    assert "Howrah" in nodes or "Murshidabad" in nodes


def test_predict_routes_west_bengal(predictor):
    profile = {
        "name": "Test Person",
        "last_seen_location": "Murshidabad",
        "state": "West Bengal",
        "district": "Murshidabad"
    }
    
    routes = predictor.predict_likely_routes(profile)
    
    assert isinstance(routes, list)
    assert len(routes) > 0
    assert routes[0]["risk_level"] in ["high", "medium", "low"]


def test_predict_routes_bihar(predictor):
    profile = {
        "name": "Test Person",
        "last_seen_location": "Patna",
        "state": "Bihar",
        "district": "Patna"
    }
    
    routes = predictor.predict_likely_routes(profile)
    assert isinstance(routes, list)
    assert len(routes) > 0


def test_predict_routes_unknown_location(predictor):
    profile = {
        "name": "Test Person",
        "last_seen_location": "Unknown City",
        "state": "Unknown State",
        "district": "Unknown"
    }
    
    routes = predictor.predict_likely_routes(profile)
    assert isinstance(routes, list)


def test_get_checkpoints(predictor):
    corridor = predictor.corridors[0]
    checkpoints = predictor.get_checkpoints(corridor)
    
    assert isinstance(checkpoints, list)
    assert len(checkpoints) > 0
    
    for checkpoint in checkpoints:
        assert "location" in checkpoint
        assert "type" in checkpoint
        assert "estimated_arrival_hours" in checkpoint
        assert "authorities_to_alert" in checkpoint


def test_activate_corridor_alert(predictor):
    profile = {
        "name": "Test Victim",
        "case_number": "DRISHTI-WB-TEST-001",
        "last_seen_location": "Murshidabad",
        "state": "West Bengal"
    }
    
    result = predictor.activate_corridor_alert(profile)
    
    assert "status" in result
    assert result["status"] in ["corridor_alert_activated", "no_routes_identified"]
    
    if result["status"] == "corridor_alert_activated":
        assert "routes_identified" in result
        assert "checkpoints_alerted" in result
        assert result["checkpoints_alerted"] > 0


def test_estimate_arrival_times_known_route(predictor):
    result = predictor.estimate_arrival_times("Murshidabad", "Howrah")
    
    assert "source" in result
    assert "destination" in result
    assert result["source"] == "Murshidabad"
    assert result["destination"] == "Howrah"


def test_estimate_arrival_times_unknown_route(predictor):
    result = predictor.estimate_arrival_times("Unknown City A", "Unknown City B")
    
    assert "source" in result
    assert "destination" in result
    assert "confidence" in result
    assert result["confidence"] == "low"


def test_high_risk_states_defined(predictor):
    assert len(predictor.high_risk_states) > 0
    assert "West Bengal" in predictor.high_risk_states
    assert "Bihar" in predictor.high_risk_states


def test_transit_hubs_defined(predictor):
    assert len(predictor.transit_hubs) > 0
