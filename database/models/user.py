from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from database.config import Base
from .enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(125), nullable=False)
    email = Column(String(250), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.MANAGEMENT)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False)

    customers = relationship("Customer", back_populates="sales")
    events = relationship("Event", back_populates="support")
