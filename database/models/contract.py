from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, Boolean
from sqlalchemy.orm import relationship
from database.config import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    remaining_amount = Column(Numeric(10, 2), nullable=False)
    is_signed = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False)

    customers_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    customer = relationship("Customer", back_populates="contracts")
    events = relationship("Event", back_populates="contract")
