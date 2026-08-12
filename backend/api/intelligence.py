"""Crowd Intelligence API endpoints.

POST /api/intelligence/analyze   — analyse observed tracks
GET  /api/intelligence/live      — return most recent intelligence state
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from schemas import (
    IntelligenceRequest,
    IntelligenceResponse,
    IntelligenceZoneState,
    BottleneckInfo,
)
from services.crowd_intelligence import (
    analyze_tracks,
    get_live_intelligence_state,
)

router = APIRouter(prefix="/api/intelligence", tags=["Intelligence"])


@router.post(
    "/analyze",
    response_model=IntelligenceResponse,
    responses={
        200: {"model": IntelligenceResponse, "description": "Analysis completed"},
        400: {"description": "Invalid input"},
    },
)
def analyze(payload: IntelligenceRequest):
    """Analyse observed tracks and return crowd intelligence."""
    if not payload.tracks:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "No tracks provided"},
        )

    tracks = [t.model_dump() for t in payload.tracks]
    result = analyze_tracks(tracks)

    zones = [IntelligenceZoneState(**z) for z in result["zones"]]
    bottlenecks = [BottleneckInfo(**b) for b in result["bottlenecks"]]

    return IntelligenceResponse(zones=zones, bottlenecks=bottlenecks)


@router.get(
    "/live",
    response_model=IntelligenceResponse,
    responses={
        200: {"model": IntelligenceResponse, "description": "Current intelligence state"},
    },
)
def get_live():
    """Return the most recent crowd intelligence state.

    If no observed track data has been analysed, returns a clean
    empty/default state.
    """
    state = get_live_intelligence_state()
    zones = [IntelligenceZoneState(**z) for z in state["zones"]]
    bottlenecks = [BottleneckInfo(**b) for b in state["bottlenecks"]]
    return IntelligenceResponse(zones=zones, bottlenecks=bottlenecks)
