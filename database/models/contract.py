from sqlalchemy import Column, ForeignKey, String, Numeric, Boolean
from sqlalchemy.orm import relationship
from database.config import Base
from database.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Contract(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "contracts"

    total_amount = Column(Numeric(10, 2), nullable=False)
    remaining_amount = Column(Numeric(10, 2), nullable=False)
    is_signed = Column(Boolean, default=False, nullable=False)

    customers_id = Column(
        String(36),
        ForeignKey("customers.id"),
        nullable=False
    )

    customer = relationship("Customer", back_populates="contracts")
    events = relationship("Event", back_populates="contract")
