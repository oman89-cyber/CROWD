from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    RouteRequest, 
    RouteResponse, 
    TicketErrorResponse, 
    CrowdAwareRouteResponse,
    RouteRecalculateRequest,
    RouteRecalculateResponse,
)
from services.ticket_service import get_ticket_by_session_id
from services.route_service import compute_route, get_graph, compute_crowd_aware_route
from services.route_reevaluation_service import recalculate_route_if_needed

router = APIRouter(prefix="/api", tags=["Routing"])


@router.post(
    "/route",
    response_model=RouteResponse,
    responses={
        200: {"model": RouteResponse, "description": "Route computed successfully"},
        404: {"model": TicketErrorResponse, "description": "Session or destination not found"},
    },
)
def get_route(
    payload: RouteRequest,
    db: Session = Depends(get_db),
):
    # Resolve session_id to a ticket
    ticket = get_ticket_by_session_id(db, payload.session_id)
    if not ticket:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"valid": False, "message": "Session not found"},
        )

    # Validate destination exists in the graph
    G = get_graph()
    if payload.destination not in G:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"valid": False, "message": "Destination not found in venue"},
        )

    # Determine starting location from ticket parking assignment
    start = ticket.parking

    result = compute_route(start, payload.destination)
    if result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"valid": False, "message": "No route exists between start and destination"},
        )

    return RouteResponse(
        route=result["route"],
        estimated_minutes=result["estimated_minutes"],
        distance=result["distance"],
        risk=0.0,
    )


@router.post(
    "/route/crowd-aware",
    response_model=CrowdAwareRouteResponse,
    responses={
        200: {"model": CrowdAwareRouteResponse, "description": "Crowd-aware route computed successfully"},
        404: {"model": TicketErrorResponse, "description": "Session or destination not found"},
    },
)
def get_crowd_aware_route(
    payload: RouteRequest,
    db: Session = Depends(get_db),
):
    # Resolve session_id to a ticket
    ticket = get_ticket_by_session_id(db, payload.session_id)
    if not ticket:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"valid": False, "message": "Session not found"},
        )

    # Validate destination exists in the graph
    G = get_graph()
    if payload.destination not in G:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"valid": False, "message": "Destination not found in venue"},
        )

    # Determine starting location from ticket parking assignment
    start = ticket.parking

    result = compute_crowd_aware_route(start, payload.destination)
    if result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"valid": False, "message": "No route exists between start and destination"},
        )

    return CrowdAwareRouteResponse(**result)


@router.post(
    "/route/recalculate",
    response_model=RouteRecalculateResponse,
    responses={
        200: {"model": RouteRecalculateResponse, "description": "Route recalculation completed"},
        404: {"model": TicketErrorResponse, "description": "Session or destination not found"},
    },
)
def recalculate_route(payload: RouteRecalculateRequest):
    """Recalculate route based on current crowd conditions."""
    result = recalculate_route_if_needed(payload.session_id, payload.destination)
    
    if not result.get("success", True):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"valid": False, "message": result.get("error", "Route recalculation failed")},
        )
    
    # Determine which route to return based on whether route changed
    if result["route_changed"]:
        current_route = result["new_route"]
    else:
        current_route = result["current_route"]
    
    return RouteRecalculateResponse(
        session_id=result["session_id"],
        route_changed=result["route_changed"],
        current_route=current_route,
        previous_route=result.get("previous_route", []),
        new_route=result.get("new_route", []),
        risk_score=result["risk_score"],
        reason=result["reason"],
        route_version=result["route_version"],
        improvement=result.get("improvement", 0.0),
    )
