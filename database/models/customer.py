import uuid
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from database.config import Base
from .base import TimestampMixin


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"

    customer_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    full_name = Column(String(125), nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    phone = Column(String(250), nullable=False)
    company_name = Column(String(250), nullable=False)

    sales_id = Column(
        String(36),
        ForeignKey("employees.employee_id"),
        nullable=False
    )

    sales = relationship("Employee", back_populates="customers")
    contracts = relationship("Contract", back_populates="customer")

    def __repr__(self):
        return f"<Customer (full_name: {self.full_name}, email: {self.email})>"
