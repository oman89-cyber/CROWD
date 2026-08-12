from sqlalchemy import Column, Integer, String
from database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True, nullable=False)
    gate = Column(String, nullable=False)
    block = Column(String, nullable=False)
    seat = Column(String, nullable=False)
    parking = Column(String, nullable=False)
    entry_window = Column(String, nullable=False)
