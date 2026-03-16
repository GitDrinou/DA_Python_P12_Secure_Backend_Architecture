import uuid
from sqlalchemy import Column, ForeignKey, String, Numeric, Boolean
from sqlalchemy.orm import relationship
from database.config import Base
from .base import TimestampMixin


class Contract(TimestampMixin, Base):
    __tablename__ = "contracts"

    contract_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    total_amount = Column(Numeric(10, 2), nullable=False)
    remaining_amount = Column(Numeric(10, 2), nullable=False)
    is_signed = Column(Boolean, default=False, nullable=False)

    customers_id = Column(
        String(36),
        ForeignKey("customers.customer_id"),
        nullable=False
    )

    customer = relationship("Customer", back_populates="contracts")
    events = relationship("Event", back_populates="contract")

    def __repr__(self):
        return (f"<Contract (id: '{self.contract_id}', total_amount = "
                f"{self.total_amount} €), remaining_amount = "
                f"{self.remaining_amount} €, is_signed ="
                f" {self.is_signed}, >")
