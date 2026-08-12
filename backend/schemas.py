from pydantic import BaseModel


class TicketVerifyRequest(BaseModel):
    ticket_id: str


class TicketVerifyResponse(BaseModel):
    valid: bool
    session_id: str
    gate: str
    block: str
    seat: str
    parking: str
    entry_window: str


class TicketErrorResponse(BaseModel):
    valid: bool = False
    message: str


class RouteRequest(BaseModel):
    session_id: str
    destination: str


class RouteResponse(BaseModel):
    route: list[str]
    estimated_minutes: float
    distance: float
    risk: float = 0.0


class CrowdAwareRouteResponse(BaseModel):
    original_route: list[str]
    recommended_route: list[str]
    distance: float
    estimated_minutes: float
    risk_score: float = 0.0
    route_mode: str
    rerouted: bool
    reason: str


class ZoneState(BaseModel):
    zone_id: str
    people: int
    capacity: int
    density: float
    incoming_flow: int
    outgoing_flow: int
    risk: float = 0.0


class SimulationRequest(BaseModel):
    crowd_size: int
    event_phase: str


class SimulationResponse(BaseModel):
    total_people: int
    event_phase: str
    zones: list[ZoneState]


class CrowdLiveResponse(BaseModel):
    total_people: int
    event_phase: str
    zones: list[ZoneState]


# ---------------------------------------------------------------------------
# Step 9: Crowd Intelligence Engine schemas
# ---------------------------------------------------------------------------

class TrackObservation(BaseModel):
    """A single anonymous track observation."""
    track_id: str
    zone_id: str
    timestamp: float


class IntelligenceRequest(BaseModel):
    """Request body for POST /api/intelligence/analyze."""
    tracks: list[TrackObservation]


class IntelligenceZoneState(BaseModel):
    """Full intelligence output for a single zone."""
    zone_id: str
    people: int
    capacity: int
    occupancy_ratio: float = 0.0
    density_ratio: float = 0.0
    density_percent: float = 0.0
    density_level: str = "LOW"
    incoming_flow: int = 0
    outgoing_flow: int = 0
    net_flow: int = 0
    risk_score: float = 0.0
    risk_level: str = "LOW"
    is_bottleneck: bool = False


class BottleneckInfo(BaseModel):
    """Bottleneck detail for a single zone."""
    zone_id: str
    is_bottleneck: bool
    reason: str = ""


class IntelligenceResponse(BaseModel):
    """Response body for intelligence endpoints."""
    zones: list[IntelligenceZoneState]
    bottlenecks: list[BottleneckInfo] = []


# ---------------------------------------------------------------------------
# Step 13: Route Re-evaluation schemas
# ---------------------------------------------------------------------------

class RouteRecalculateRequest(BaseModel):
    """Request body for POST /api/route/recalculate."""
    session_id: str
    destination: str


class RouteRecalculateResponse(BaseModel):
    """Response body for route recalculation."""
    session_id: str
    route_changed: bool
    current_route: list[str] = []
    previous_route: list[str] = []
    new_route: list[str] = []
    risk_score: float = 0.0
    reason: str = ""
    route_version: int = 1
    improvement: float = 0.0
