from datetime import datetime, timezone
from sqlalchemy import (Column, Integer, String, ForeignKey, Text,
                        DateTime)
from sqlalchemy.orm import relationship
from database.config import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    start_date = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False)
    end_date = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    location = Column(String(255), nullable=False)
    attendees = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False)

    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    support_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contract = relationship("Contract", back_populates="events")
    support = relationship("User", back_populates="events")
