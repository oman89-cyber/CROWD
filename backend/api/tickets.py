from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from schemas import TicketVerifyRequest, TicketVerifyResponse, TicketErrorResponse
from services.ticket_service import get_ticket_by_id, generate_session_id

router = APIRouter(prefix="/api/ticket", tags=["Tickets"])


@router.post(
    "/verify",
    response_model=TicketVerifyResponse,
    responses={
        200: {"model": TicketVerifyResponse, "description": "Ticket verified successfully"},
        404: {"model": TicketErrorResponse, "description": "Ticket not found"},
    },
)
def verify_ticket(
    payload: TicketVerifyRequest,
    db: Session = Depends(get_db),
):
    ticket = get_ticket_by_id(db, payload.ticket_id)
    if not ticket:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"valid": False, "message": "Ticket not found"},
        )

    session_id = generate_session_id(ticket)

    return TicketVerifyResponse(
        valid=True,
        session_id=session_id,
        gate=ticket.gate,
        block=ticket.block,
        seat=ticket.seat,
        parking=ticket.parking,
        entry_window=ticket.entry_window,
    )
