import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.config import Base
from .base import TimestampMixin


class Employee(TimestampMixin, Base):
    __tablename__ = "employees"

    employee_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    full_name = Column(String(125), nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    role_id = Column(String(36), ForeignKey("roles.role_id"), nullable=False)

    role = relationship("Role", back_populates="employees")
    customers = relationship("Customer", back_populates="sales")
    events = relationship("Event", back_populates="support")

    def __repr__(self):
        return f"<Employee (full_name: {self.full_name}, email: {self.email})>"
