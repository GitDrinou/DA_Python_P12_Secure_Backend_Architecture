from sqlalchemy import Column, String, Enum, Boolean
from sqlalchemy.orm import relationship
from database.config import Base
from .base import UUIDPrimaryKeyMixin, TimestampMixin
from .enums import EmployeeRole


class Employee(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "employees"

    full_name = Column(String(125), nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum(EmployeeRole),
        nullable=False,
        default=EmployeeRole.MANAGEMENT
    )
    is_active = Column(Boolean, default=True, nullable=False)

    customers = relationship("Customer", back_populates="sales")
    events = relationship("Event", back_populates="support")
