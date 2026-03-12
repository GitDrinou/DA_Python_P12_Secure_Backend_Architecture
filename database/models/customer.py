from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, String, DateTime, Integer
from sqlalchemy.orm import relationship
from database.config import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(125), nullable=False)
    email = Column(String(250), unique=True, nullable=False, index=True)
    phone = Column(String(250), nullable=False)
    company_name = Column(String(250), nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc))

    sales_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sales = relationship("User", back_populates="customers")
    contracts = relationship("Contract", back_populates="customer")
