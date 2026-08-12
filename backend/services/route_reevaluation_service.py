"""Route Re-evaluation Service — determines when active routes need recalculation.

This service monitors crowd intelligence changes and decides whether an active
user's route should be recalculated based on configurable risk thresholds
and improvement criteria.

Architecture:
    LIVE VIDEO → CROWD INTELLIGENCE → RISK CHANGE → ROUTE RE-EVALUATION
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from services.crowd_intelligence import get_live_intelligence_state
from services.route_service import compute_crowd_aware_route, get_graph

# ---------------------------------------------------------------------------
# Configuration Constants
# ---------------------------------------------------------------------------

# Risk threshold above which rerouting is considered
REROUTE_RISK_THRESHOLD = 0.60

# Minimum improvement required to trigger reroute (10% cost reduction)
REROUTE_IMPROVEMENT_THRESHOLD = 0.10

# Cooldown period to prevent route oscillation (seconds)
REROUTE_COOLDOWN_SECONDS = 15

# Critical risk level that can bypass cooldown
CRITICAL_RISK_THRESHOLD = 0.80

# ---------------------------------------------------------------------------
# Active Route State Management
# ---------------------------------------------------------------------------

@dataclass
class ActiveRouteState:
    """In-memory state for an active user route."""
    
    session_id: str
    destination: str
    current_route: list[str] = field(default_factory=list)
    last_route_update: float = field(default_factory=time.time)
    last_risk_score: float = 0.0
    route_version: int = 1
    
    def can_reroute(self) -> bool:
        """Check if enough time has passed since last reroute."""
        return time.time() - self.last_route_update >= REROUTE_COOLDOWN_SECONDS
    
    def update_route(self, new_route: list[str], risk_score: float) -> None:
        """Update the route state with new route and metadata."""
        self.current_route = new_route
        self.last_route_update = time.time()
        self.last_risk_score = risk_score
        self.route_version += 1


# In-memory storage for active routes (MVP implementation)
_active_routes: Dict[str, ActiveRouteState] = {}


def get_active_route_state(session_id: str, destination: str) -> ActiveRouteState:
    """Get or create active route state for a session."""
    key = f"{session_id}:{destination}"
    
    if key not in _active_routes:
        _active_routes[key] = ActiveRouteState(
            session_id=session_id,
            destination=destination,
        )
    
    return _active_routes[key]


def clear_active_route_state(session_id: str, destination: str) -> None:
    """Clear active route state (for testing/cleanup)."""
    key = f"{session_id}:{destination}"
    _active_routes.pop(key, None)


# ---------------------------------------------------------------------------
# Route Risk Analysis
# ---------------------------------------------------------------------------

def analyze_route_risk(route: list[str]) -> dict:
    """Analyze the current crowd risk along a route path.
    
    Returns:
        dict: {
            "max_risk": float,
            "max_risk_zone": str,
            "high_risk_zones": list[str],
            "bottleneck_zones": list[str],
        }
    """
    intelligence_state = get_live_intelligence_state()
    zones = intelligence_state.get("zones", [])
    
    # Create risk lookup
    risk_lookup = {z["zone_id"]: z.get("risk_score", 0.0) for z in zones}
    
    # Find zones on route that are high risk or bottlenecks
    high_risk_zones = []
    bottleneck_zones = []
    max_risk = 0.0
    max_risk_zone = ""
    
    for zone_id in route:
        risk_score = risk_lookup.get(zone_id, 0.0)
        
        if risk_score > max_risk:
            max_risk = risk_score
            max_risk_zone = zone_id
            
        if risk_score >= REROUTE_RISK_THRESHOLD:
            high_risk_zones.append(zone_id)
            
        # Check if zone is marked as bottleneck
        for zone_data in zones:
            if zone_data["zone_id"] == zone_id and zone_data.get("is_bottleneck", False):
                bottleneck_zones.append(zone_id)
                break
    
    return {
        "max_risk": max_risk,
        "max_risk_zone": max_risk_zone,
        "high_risk_zones": high_risk_zones,
        "bottleneck_zones": bottleneck_zones,
    }


def should_reroute(
    current_route: list[str],
    latest_crowd_state: dict,
    route_state: ActiveRouteState,
) -> tuple[bool, str]:
    """Determine if a route should be recalculated based on crowd conditions.
    
    Args:
        current_route: Current route path
        latest_crowd_state: Latest intelligence state
        route_state: Active route state with cooldown info
        
    Returns:
        tuple: (should_reroute: bool, reason: str)
    """
    # Analyze current route risk
    risk_analysis = analyze_route_risk(current_route)
    max_risk = risk_analysis["max_risk"]
    high_risk_zones = risk_analysis["high_risk_zones"]
    bottleneck_zones = risk_analysis["bottleneck_zones"]
    
    # Check if any zone on route exceeds risk threshold
    if not high_risk_zones and not bottleneck_zones:
        return False, "Current route risk within acceptable limits"
    
    # Check cooldown (unless critical risk)
    if max_risk < CRITICAL_RISK_THRESHOLD and not route_state.can_reroute():
        remaining_cooldown = REROUTE_COOLDOWN_SECONDS - (time.time() - route_state.last_route_update)
        return False, f"Reroute cooldown active ({remaining_cooldown:.1f}s remaining)"
    
    # Generate reason based on risk conditions
    reason_parts = []
    
    if high_risk_zones:
        if len(high_risk_zones) == 1:
            reason_parts.append(f"{high_risk_zones[0]} became high-risk")
        else:
            reason_parts.append(f"Multiple zones became high-risk: {', '.join(high_risk_zones)}")
    
    if bottleneck_zones:
        if len(bottleneck_zones) == 1:
            reason_parts.append(f"{bottleneck_zones[0]} is a bottleneck")
        else:
            reason_parts.append(f"Multiple bottlenecks: {', '.join(bottleneck_zones)}")
    
    reason = "; ".join(reason_parts)
    
    if max_risk >= CRITICAL_RISK_THRESHOLD:
        reason += " (critical risk - bypassing cooldown)"
    
    return True, reason


# ---------------------------------------------------------------------------
# Route Recalculation
# ---------------------------------------------------------------------------

def recalculate_route_if_needed(
    session_id: str,
    destination: str,
) -> dict:
    """Recalculate route if crowd conditions warrant it.
    
    Returns:
        dict: Route recalculation response with routing decision
    """
    # Get active route state
    route_state = get_active_route_state(session_id, destination)
    
    # Get latest crowd intelligence
    intelligence_state = get_live_intelligence_state()
    
    # Calculate current crowd-aware route
    from services.ticket_service import get_ticket_by_session_id
    from database import get_db
    
    # Get database session (simplified for MVP)
    try:
        db = next(get_db())
        ticket = get_ticket_by_session_id(db, session_id)
        
        if not ticket:
            return {
                "success": False,
                "error": "Session not found",
            }
        
        start = ticket.parking
        db.close()
    except Exception as e:
        # Fallback for testing - use default parking
        print(f"Database access failed, using fallback: {e}")
        start = "P3"  # Default parking for CS-1021
    
    # Validate destination exists
    graph = get_graph()
    if destination not in graph:
        return {
            "success": False,
            "error": "Destination not found in venue",
        }
    
    # Get current optimal route
    current_route_result = compute_crowd_aware_route(start, destination)
    if not current_route_result:
        return {
            "success": False,
            "error": "No route exists between start and destination",
        }
    
    current_optimal_route = current_route_result["recommended_route"]
    
    # If this is the first route calculation, store it and return
    if not route_state.current_route:
        route_state.update_route(current_optimal_route, current_route_result["risk_score"])
        return {
            "session_id": session_id,
            "route_changed": False,
            "current_route": current_optimal_route,
            "risk_score": current_route_result["risk_score"],
            "reason": "Initial route calculation",
            "route_version": route_state.route_version,
        }
    
    # Check if rerouting is needed
    needs_reroute, reroute_reason = should_reroute(
        route_state.current_route,
        intelligence_state,
        route_state,
    )
    
    if not needs_reroute:
        return {
            "session_id": session_id,
            "route_changed": False,
            "current_route": route_state.current_route,
            "risk_score": route_state.last_risk_score,
            "reason": reroute_reason,
            "route_version": route_state.route_version,
        }
    
    # Check if new route is meaningfully better
    if current_optimal_route == route_state.current_route:
        return {
            "session_id": session_id,
            "route_changed": False,
            "current_route": route_state.current_route,
            "risk_score": current_route_result["risk_score"],
            "reason": "Current route is still optimal",
            "route_version": route_state.route_version,
        }
    
    # Calculate improvement (simplified - could use dynamic cost comparison)
    current_risk = analyze_route_risk(route_state.current_route)["max_risk"]
    new_risk = analyze_route_risk(current_optimal_route)["max_risk"]
    
    improvement = 0.0
    if current_risk > 0:
        improvement = (current_risk - new_risk) / current_risk
        if improvement < REROUTE_IMPROVEMENT_THRESHOLD and new_risk < REROUTE_RISK_THRESHOLD:
            return {
                "session_id": session_id,
                "route_changed": False,
                "current_route": route_state.current_route,
                "risk_score": route_state.last_risk_score,
                "reason": "Alternative route improvement insufficient",
                "route_version": route_state.route_version,
            }
    
    # Route change approved - update state
    previous_route = route_state.current_route.copy()
    route_state.update_route(current_optimal_route, current_route_result["risk_score"])
    
    return {
        "session_id": session_id,
        "route_changed": True,
        "previous_route": previous_route,
        "new_route": current_optimal_route,
        "risk_score": current_route_result["risk_score"],
        "reason": reroute_reason,
        "route_version": route_state.route_version,
        "improvement": improvement,
    }


# ---------------------------------------------------------------------------
# Demo/Testing Utilities
# ---------------------------------------------------------------------------

def create_demo_high_risk_state(zone_id: str, risk_score: float = 0.85) -> None:
    """Create a demo state with high risk in specified zone (for testing)."""
    from services.crowd_intelligence import set_live_intelligence_state, ZONE_CAPACITY
    
    # Create demo state with high risk in specified zone
    zones = []
    for zid, capacity in ZONE_CAPACITY.items():
        if zid == zone_id:
            # High risk zone
            zones.append({
                "zone_id": zid,
                "people": int(capacity * 0.8),  # 80% capacity
                "capacity": capacity,
                "occupancy_ratio": 0.8,
                "density_ratio": 0.8,
                "density_percent": 80.0,
                "density_level": "HIGH",
                "incoming_flow": 50,
                "outgoing_flow": 10,
                "net_flow": 40,
                "risk_score": risk_score,
                "risk_level": "CRITICAL" if risk_score >= 0.80 else "HIGH",
                "is_bottleneck": True,
            })
        else:
            # Normal zones
            zones.append({
                "zone_id": zid,
                "people": int(capacity * 0.1),  # 10% capacity
                "capacity": capacity,
                "occupancy_ratio": 0.1,
                "density_ratio": 0.1,
                "density_percent": 10.0,
                "density_level": "LOW",
                "incoming_flow": 2,
                "outgoing_flow": 3,
                "net_flow": -1,
                "risk_score": 0.05,
                "risk_level": "LOW",
                "is_bottleneck": False,
            })
    
    demo_state = {
        "zones": zones,
        "bottlenecks": [{"zone_id": zone_id, "is_bottleneck": True, "reason": f"High density ({risk_score:.0%}) in demo mode"}]
    }
    
    set_live_intelligence_state(demo_state)


def reset_demo_state() -> None:
    """Reset to normal/low-risk state (for testing)."""
    from services.crowd_intelligence import set_live_intelligence_state, ZONE_CAPACITY
    
    zones = []
    for zid, capacity in ZONE_CAPACITY.items():
        zones.append({
            "zone_id": zid,
            "people": int(capacity * 0.05),  # 5% capacity
            "capacity": capacity,
            "occupancy_ratio": 0.05,
            "density_ratio": 0.05,
            "density_percent": 5.0,
            "density_level": "LOW",
            "incoming_flow": 1,
            "outgoing_flow": 1,
            "net_flow": 0,
            "risk_score": 0.02,
            "risk_level": "LOW",
            "is_bottleneck": False,
        })
    
    normal_state = {
        "zones": zones,
        "bottlenecks": []
    }
    
    set_live_intelligence_state(normal_state)