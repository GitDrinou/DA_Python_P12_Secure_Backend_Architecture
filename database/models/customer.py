from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from database.config import Base
from database.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Customer(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "customers"

    full_name = Column(String(125), nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    phone = Column(String(250), nullable=False)
    company_name = Column(String(250), nullable=False)

    sales_id = Column(String(36), ForeignKey("employees.id"), nullable=False)

    sales = relationship("Employee", back_populates="customers")
    contracts = relationship("Contract", back_populates="customer")
