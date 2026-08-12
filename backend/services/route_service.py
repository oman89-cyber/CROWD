"""Route service — loads the venue graph and provides shortest-path routing."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Optional

import networkx as nx

# ---------------------------------------------------------------------------
# Walking speed assumption: ~1.2 m/s (relaxed crowd walking pace)
# ---------------------------------------------------------------------------
WALKING_SPEED_MPS = 1.2

# ---------------------------------------------------------------------------
# Graph loading
# ---------------------------------------------------------------------------
_VENUE_JSON = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, "data", "venue.json"
)


@lru_cache(maxsize=1)
def _load_venue_graph() -> nx.Graph:
    """Load venue.json and build an undirected NetworkX graph (cached)."""
    path = os.path.normpath(_VENUE_JSON)
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    G = nx.Graph()

    for node in data["nodes"]:
        G.add_node(node["id"], type=node["type"], name=node["name"])

    for edge in data["edges"]:
        G.add_edge(
            edge["from"],
            edge["to"],
            distance=edge["distance"],
            capacity=edge["capacity"],
        )

    return G


def get_graph() -> nx.Graph:
    """Public accessor for the venue graph."""
    return _load_venue_graph()


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def _heuristic(_u: str, _v: str) -> float:
    """Admissible heuristic for A*.

    Because we don't have real coordinates, return 0 — this degrades A* to
    Dijkstra but keeps the interface ready for a coordinate-aware heuristic
    later.
    """
    return 0


def compute_route(
    start: str,
    destination: str,
) -> Optional[dict]:
    """Compute shortest path between *start* and *destination*.

    Returns a dict with keys ``route``, ``distance``, and
    ``estimated_minutes``, or *None* if no path exists.
    """
    G = get_graph()

    if start not in G:
        return None
    if destination not in G:
        return None

    try:
        path = nx.astar_path(G, start, destination, heuristic=_heuristic, weight="distance")
    except nx.NetworkXNoPath:
        return None

    total_distance = sum(
        G[path[i]][path[i + 1]]["distance"] for i in range(len(path) - 1)
    )

    estimated_seconds = total_distance / WALKING_SPEED_MPS
    estimated_minutes = round(estimated_seconds / 60, 1)

    return {
        "route": path,
        "distance": total_distance,
        "estimated_minutes": estimated_minutes,
    }


# ---------------------------------------------------------------------------
# Crowd-Aware Routing
# ---------------------------------------------------------------------------

# Dynamic cost configuration
RISK_WEIGHT = 4.0
MIN_ROUTE_IMPROVEMENT = 0.10


def calculate_dynamic_cost(distance: float, risk: float) -> float:
    """Calculate edge cost balancing physical distance and crowd risk."""
    return distance * (1.0 + RISK_WEIGHT * risk)


def _get_edge_risk(u: str, v: str, risk_lookup: dict[str, float]) -> float:
    """Map an edge to the relevant zone risk.
    
    Since the graph is undirected and people traverse both zones, we take the 
    maximum risk of the two endpoints to penalize edges connected to crowded zones.
    """
    return max(risk_lookup.get(u, 0.0), risk_lookup.get(v, 0.0))


def compute_crowd_aware_route(
    start: str,
    destination: str,
) -> Optional[dict]:
    """Compute a route that balances distance and crowd risk."""
    from services.crowd_intelligence import get_live_intelligence_state
    
    G = get_graph()

    if start not in G or destination not in G:
        return None

    # 1. Calculate static shortest route
    static_result = compute_route(start, destination)
    if not static_result:
        return None
        
    static_path = static_result["route"]

    # 2. Retrieve latest crowd intelligence
    intelligence_state = get_live_intelligence_state()
    zones = intelligence_state.get("zones", [])
    
    # 3. No-crowd fallback
    # If no track data has been analysed, zones have 0 occupancy or it's empty
    if not zones or all(z.get("people", 0) == 0 for z in zones):
        return {
            "original_route": static_path,
            "recommended_route": static_path,
            "distance": static_result["distance"],
            "estimated_minutes": static_result["estimated_minutes"],
            "risk_score": 0.0,
            "route_mode": "static_fallback",
            "rerouted": False,
            "reason": "No crowd intelligence data available"
        }

    # 4. Map risks
    risk_lookup = {z["zone_id"]: z.get("risk_score", 0.0) for z in zones}

    # 5. Define dynamic weight function for A*
    def weight_func(u, v, d):
        distance = d["distance"]
        edge_risk = _get_edge_risk(u, v, risk_lookup)
        return calculate_dynamic_cost(distance, edge_risk)
        
    # 6. Run A* with dynamic costs
    try:
        crowd_aware_path = nx.astar_path(G, start, destination, heuristic=_heuristic, weight=weight_func)
    except nx.NetworkXNoPath:
        return None

    # Helper to calculate the total dynamic cost of a given path
    def calculate_path_dynamic_cost(path: list[str]) -> float:
        cost = 0.0
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            d = G[u][v]["distance"]
            edge_risk = _get_edge_risk(u, v, risk_lookup)
            cost += calculate_dynamic_cost(d, edge_risk)
        return cost
        
    static_dynamic_cost = calculate_path_dynamic_cost(static_path)
    crowd_aware_dynamic_cost = calculate_path_dynamic_cost(crowd_aware_path)
    
    # 7. Decide whether to reroute
    rerouted = False
    reason = "Original route is optimal"
    
    if static_dynamic_cost > 0:
        improvement = (static_dynamic_cost - crowd_aware_dynamic_cost) / static_dynamic_cost
        # Only reroute if paths differ and improvement meets threshold
        if crowd_aware_path != static_path and improvement >= MIN_ROUTE_IMPROVEMENT:
            rerouted = True
            
            # Formulate a helpful reason based on high-risk bottlenecks in the original route
            high_risk_zones = [node for node in static_path if risk_lookup.get(node, 0.0) >= 0.60]
            if high_risk_zones:
                reason = f"Original route contains a high-risk bottleneck: {', '.join(high_risk_zones)}"
            else:
                reason = "Alternative route has significantly lower dynamic cost"

    recommended_route = crowd_aware_path if rerouted else static_path

    # Calculate actual metrics for the recommended route
    total_distance = sum(
        G[recommended_route[i]][recommended_route[i + 1]]["distance"] 
        for i in range(len(recommended_route) - 1)
    )
    estimated_seconds = total_distance / WALKING_SPEED_MPS
    estimated_minutes = round(estimated_seconds / 60, 1)
    max_risk = max([risk_lookup.get(node, 0.0) for node in recommended_route] + [0.0])

    return {
        "original_route": static_path,
        "recommended_route": recommended_route,
        "distance": total_distance,
        "estimated_minutes": estimated_minutes,
        "risk_score": max_risk,
        "route_mode": "crowd_aware",
        "rerouted": rerouted,
        "reason": reason
    }
