"""
Module 2: Trafficking Route Predictor

Uses NetworkX graph analysis to model known trafficking corridors
and predict likely movement routes.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

import networkx as nx

logger = logging.getLogger(__name__)

TRAFFICKING_ROUTES = {
    "corridors": [
        {
            "source": "Murshidabad",
            "transit_hubs": ["Malda", "Kolkata", "Howrah", "Sealdah"],
            "destinations": ["Delhi", "Mumbai", "Punjab"],
            "time_windows": {
                "Murshidabad → Howrah": {"min_hours": 4, "max_hours": 6},
                "Howrah → Delhi": {"min_hours": 17, "max_hours": 24},
                "Howrah → Mumbai": {"min_hours": 26, "max_hours": 32}
            },
            "common_methods": ["train", "private_vehicle", "bus"],
            "risk_level": "high"
        },
        {
            "source": "Bihar",
            "transit_hubs": ["Patna", "Varanasi", "Allahabad"],
            "destinations": ["Delhi", "Haryana", "Punjab", "Mumbai"],
            "time_windows": {
                "Patna → Delhi": {"min_hours": 12, "max_hours": 16},
                "Patna → Mumbai": {"min_hours": 24, "max_hours": 30}
            },
            "common_methods": ["train", "bus"],
            "risk_level": "high"
        },
        {
            "source": "Jharkhand",
            "transit_hubs": ["Ranchi", "Dhanbad", "Kolkata"],
            "destinations": ["Delhi", "Haryana", "Punjab"],
            "time_windows": {
                "Ranchi → Delhi": {"min_hours": 18, "max_hours": 22}
            },
            "common_methods": ["train", "private_vehicle"],
            "risk_level": "high"
        },
        {
            "source": "Odisha",
            "transit_hubs": ["Bhubaneswar", "Cuttack", "Kolkata"],
            "destinations": ["Delhi", "Surat", "Mumbai"],
            "time_windows": {
                "Bhubaneswar → Delhi": {"min_hours": 24, "max_hours": 28}
            },
            "common_methods": ["train", "bus"],
            "risk_level": "medium"
        },
        {
            "source": "Rajasthan",
            "transit_hubs": ["Jaipur", "Jodhpur", "Delhi"],
            "destinations": ["Mumbai", "Surat", "Gulf Countries"],
            "time_windows": {
                "Jaipur → Mumbai": {"min_hours": 14, "max_hours": 18}
            },
            "common_methods": ["train", "bus", "flight"],
            "risk_level": "medium"
        }
    ],
    "high_risk_states": [
        "West Bengal", "Bihar", "Jharkhand", "Odisha", "Rajasthan",
        "Uttar Pradesh", "Assam", "Chhattisgarh"
    ],
    "major_transit_hubs": [
        "Howrah", "Sealdah", "New Delhi", "Mumbai CST",
        "Chennai Central", "Patna Junction", "Varanasi Junction",
        "Kolkata Airport", "Delhi Airport", "Mumbai Airport"
    ],
    "border_crossing_points": [
        "Petrapole", "Gede", "Haridaspur", "Changrabandha",
        "Fulbari", "Banglabandha"
    ]
}


class RoutePredictor:
    """
    Predicts trafficking routes using graph-based analysis
    of known corridors and historical patterns.
    """

    def __init__(self):
        self.route_graph = nx.DiGraph()
        self.corridors = TRAFFICKING_ROUTES["corridors"]
        self.high_risk_states = TRAFFICKING_ROUTES["high_risk_states"]
        self.transit_hubs = TRAFFICKING_ROUTES["major_transit_hubs"]
        self.build_route_graph()

    def build_route_graph(self) -> nx.DiGraph:
        """Build NetworkX directed graph of trafficking routes."""
        self.route_graph.clear()
        
        for corridor in self.corridors:
            source = corridor["source"]
            destinations = corridor["destinations"]
            hubs = corridor["transit_hubs"]
            risk = corridor["risk_level"]
            
            # Add source → first hub
            if hubs:
                self.route_graph.add_edge(
                    source, hubs[0],
                    risk=risk,
                    methods=corridor["common_methods"],
                    type="source_to_hub"
                )
                
                # Chain hubs together
                for i in range(len(hubs) - 1):
                    time_key = f"{hubs[i]} \u2192 {hubs[i+1]}"
                    time_window = corridor.get("time_windows", {}).get(time_key, {"min_hours": 2, "max_hours": 6})
                    self.route_graph.add_edge(
                        hubs[i], hubs[i+1],
                        risk=risk,
                        methods=corridor["common_methods"],
                        time_window=time_window,
                        type="hub_to_hub"
                    )
            
            # Add last hub → destinations
            last_hub = hubs[-1] if hubs else source
            for dest in destinations:
                self.route_graph.add_edge(
                    last_hub, dest,
                    risk=risk,
                    methods=corridor["common_methods"],
                    type="hub_to_destination"
                )
        
        logger.info(f"Route graph built: {self.route_graph.number_of_nodes()} nodes, "
                    f"{self.route_graph.number_of_edges()} edges")
        return self.route_graph

    def predict_likely_routes(self, missing_person_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Predict likely trafficking routes based on source location.
        Returns ranked list of probable routes.
        """
        source_location = missing_person_profile.get("last_seen_location", "")
        state = missing_person_profile.get("state", "")
        
        likely_routes = []
        
        # Find matching corridors
        for corridor in self.corridors:
            if (corridor["source"].lower() in source_location.lower() or
                    corridor["source"].lower() in state.lower()):
                
                route = {
                    "corridor": corridor,
                    "source": corridor["source"],
                    "transit_hubs": corridor["transit_hubs"],
                    "destinations": corridor["destinations"],
                    "risk_level": corridor["risk_level"],
                    "methods": corridor["common_methods"],
                    "time_windows": corridor.get("time_windows", {}),
                    "checkpoints": self.get_checkpoints(corridor),
                    "priority": "high" if corridor["risk_level"] == "high" else "medium"
                }
                likely_routes.append(route)
        
        # If no exact match, suggest based on high-risk state
        if not likely_routes and state in self.high_risk_states:
            likely_routes.append({
                "corridor": None,
                "source": state,
                "transit_hubs": ["Nearest major junction"],
                "destinations": ["Delhi", "Mumbai"],
                "risk_level": "medium",
                "methods": ["train", "bus"],
                "time_windows": {},
                "checkpoints": self.transit_hubs[:3],
                "priority": "medium",
                "note": "Generic high-risk state route"
            })
        
        return likely_routes

    def get_checkpoints(self, corridor: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of checkpoints to alert along a route."""
        checkpoints = []
        
        all_stops = [corridor["source"]] + corridor["transit_hubs"] + corridor["destinations"]
        time_windows = corridor.get("time_windows", {})
        
        cumulative_hours = 0
        for i, stop in enumerate(all_stops):
            # Estimate cumulative travel time
            if i > 0:
                route_key = f"{all_stops[i-1]} \u2192 {stop}"
                window = time_windows.get(route_key, {"min_hours": 2, "max_hours": 6})
                cumulative_hours += window.get("min_hours", 2)
            
            is_transit_hub = stop in self.transit_hubs
            checkpoints.append({
                "location": stop,
                "type": "transit_hub" if is_transit_hub else "waypoint",
                "estimated_arrival_hours": cumulative_hours,
                "authorities_to_alert": self._get_local_authorities(stop),
                "priority": "critical" if is_transit_hub else "normal"
            })
        
        return checkpoints

    def _get_local_authorities(self, location: str) -> List[str]:
        """Get list of authorities to alert at a given location."""
        authorities = ["Local Police"]
        
        if location in self.transit_hubs:
            if "Howrah" in location or "Sealdah" in location or "Junction" in location:
                authorities.extend(["Railway Protection Force (RPF)", "GRP"])
            if "Airport" in location:
                authorities.extend(["CISF", "Airport Security"])
            authorities.append("Anti-Human Trafficking Unit (AHTU)")
        
        return authorities

    def activate_corridor_alert(self, missing_person_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Full corridor alert activation workflow.
        Notifies all checkpoints along predicted routes.
        """
        routes = self.predict_likely_routes(missing_person_profile)
        
        if not routes:
            return {
                "status": "no_routes_identified",
                "message": "No known trafficking corridors match this location",
                "profile": missing_person_profile
            }
        
        alerts_sent = []
        for route in routes:
            for checkpoint in route.get("checkpoints", []):
                alert = {
                    "checkpoint": checkpoint["location"],
                    "authorities": checkpoint["authorities_to_alert"],
                    "estimated_arrival": checkpoint["estimated_arrival_hours"],
                    "priority": checkpoint["priority"],
                    "person_name": missing_person_profile.get("name", "Unknown"),
                    "case_number": missing_person_profile.get("case_number", ""),
                    "alert_sent": True
                }
                alerts_sent.append(alert)
        
        return {
            "status": "corridor_alert_activated",
            "routes_identified": len(routes),
            "checkpoints_alerted": len(alerts_sent),
            "alerts": alerts_sent,
            "activation_time": datetime.utcnow().isoformat()
        }

    def estimate_arrival_times(self, source: str, destination: str) -> Dict[str, Any]:
        """Predict when victim might arrive at destination."""
        try:
            if nx.has_path(self.route_graph, source, destination):
                path = nx.shortest_path(self.route_graph, source, destination)
                
                total_min = 0
                total_max = 0
                
                for corridor in self.corridors:
                    for time_key, window in corridor.get("time_windows", {}).items():
                        src, dst = time_key.split(" \u2192 ")
                        if src in path and dst in path:
                            total_min += window.get("min_hours", 0)
                            total_max += window.get("max_hours", 0)
                
                if total_min == 0:
                    total_min, total_max = 12, 24  # Default estimate
                
                now = datetime.utcnow()
                return {
                    "source": source,
                    "destination": destination,
                    "path": path,
                    "min_hours": total_min,
                    "max_hours": total_max,
                    "earliest_arrival": (now + timedelta(hours=total_min)).isoformat(),
                    "latest_arrival": (now + timedelta(hours=total_max)).isoformat(),
                    "confidence": "medium"
                }
        except (nx.NetworkXError, nx.exception.NodeNotFound):
            pass
        
        return {
            "source": source,
            "destination": destination,
            "path": [],
            "min_hours": None,
            "max_hours": None,
            "earliest_arrival": None,
            "latest_arrival": None,
            "confidence": "low",
            "note": "No known route between these locations"
        }
