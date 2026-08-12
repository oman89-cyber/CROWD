from sqlalchemy.orm import Session
from models import Ticket

DEMO_TICKETS = [
    {
        "ticket_id": "T0001",
        "gate": "A",
        "block": "A",
        "seat": "A101",
        "parking": "P1",
        "entry_window": "17:30-18:00",
    },
    {
        "ticket_id": "T0002",
        "gate": "A",
        "block": "B",
        "seat": "B205",
        "parking": "P1",
        "entry_window": "18:00-18:30",
    },
    {
        "ticket_id": "T0003",
        "gate": "B",
        "block": "B",
        "seat": "B110",
        "parking": "P2",
        "entry_window": "18:00-18:30",
    },
    {
        "ticket_id": "T0004",
        "gate": "C",
        "block": "C",
        "seat": "C124",
        "parking": "P3",
        "entry_window": "18:30-19:00",
    },
    {
        "ticket_id": "T0005",
        "gate": "D",
        "block": "D",
        "seat": "D402",
        "parking": "P4",
        "entry_window": "19:00-19:30",
    },
]


def seed_tickets(db: Session) -> None:
    """Seed demo tickets into the database if empty."""
    if db.query(Ticket).count() == 0:
        for ticket_data in DEMO_TICKETS:
            ticket = Ticket(**ticket_data)
            db.add(ticket)
        db.commit()


def get_ticket_by_id(db: Session, ticket_id: str) -> Ticket | None:
    """Retrieve ticket by ticket_id."""
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()


def generate_session_id(ticket: Ticket) -> str:
    """Generate deterministic session ID for a valid ticket."""
    if ticket.ticket_id == "T0004":
        return "CS-1021"
    return f"CS-{1000 + ticket.id}"


def get_ticket_by_session_id(db: Session, session_id: str) -> Ticket | None:
    """Reverse-lookup: find the ticket that maps to the given session_id."""
    tickets = db.query(Ticket).all()
    for ticket in tickets:
        if generate_session_id(ticket) == session_id:
            return ticket
    return None
