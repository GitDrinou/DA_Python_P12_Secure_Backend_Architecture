from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database.config import Base
from database.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Event(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "events"

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
        ForeignKey("contracts.id"),
        nullable=False
    )
    support_id = Column(String(36), ForeignKey("employees.id"), nullable=False)

    contract = relationship("Contract", back_populates="events")
    support = relationship("Employee", back_populates="events")
