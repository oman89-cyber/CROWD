"""Crowd and simulation API endpoints."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from schemas import (
    SimulationRequest,
    SimulationResponse,
    CrowdLiveResponse,
    ZoneState,
)
from services.crowd_service import simulate_crowd, get_live_crowd_state, set_live_crowd_state, VALID_PHASES

router = APIRouter(prefix="/api", tags=["Crowd"])


@router.post(
    "/simulation",
    response_model=SimulationResponse,
    responses={
        200: {"model": SimulationResponse, "description": "Simulation completed"},
        400: {"description": "Invalid event_phase"},
    },
)
def run_simulation(payload: SimulationRequest):
    """Run a deterministic crowd simulation for the given parameters."""
    phase = payload.event_phase.upper()
    if phase not in VALID_PHASES:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": f"Invalid event_phase '{payload.event_phase}'. "
                           f"Valid phases: {VALID_PHASES}",
            },
        )

    result = simulate_crowd(payload.crowd_size, phase)

    # Update the live crowd state so GET /api/crowd/live reflects it
    set_live_crowd_state(result)

    zones = [ZoneState(**z) for z in result["zones"]]
    return SimulationResponse(
        total_people=result["total_people"],
        event_phase=result["event_phase"],
        zones=zones,
    )


@router.get(
    "/crowd/live",
    response_model=CrowdLiveResponse,
    responses={
        200: {"model": CrowdLiveResponse, "description": "Current crowd state"},
    },
)
def get_crowd_live():
    """Return the current live crowd state."""
    state = get_live_crowd_state()
    zones = [ZoneState(**z) for z in state["zones"]]
    return CrowdLiveResponse(
        total_people=state["total_people"],
        event_phase=state["event_phase"],
        zones=zones,
    )
