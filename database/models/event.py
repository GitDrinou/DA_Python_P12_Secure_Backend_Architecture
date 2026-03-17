import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database.config import Base
from database.models.base import TimestampMixin


class Event(TimestampMixin, Base):
    __tablename__ = "events"

    event_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    title = Column(String(255), nullable=False)
    start_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False)
    end_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    location = Column(String(255), nullable=False)
    attendees = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)

    contract_id = Column(
        String(36),
        ForeignKey("contracts.contract_id"),
        nullable=False
    )
    support_id = Column(
        String(36),
        ForeignKey("employees.employee_id"),
        nullable=True
    )

    contract = relationship("Contract", back_populates="events")
    support = relationship("Employee", back_populates="events")

    def __repr__(self):
        return (f"<Event (title: {self.title}, start_date: {self.start_date}, "
                f"end_date: {self.end_date})>")
