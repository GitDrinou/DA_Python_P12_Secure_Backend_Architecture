import uuid
from sqlalchemy import String, Column
from sqlalchemy.orm import relationship
from .base import TimestampMixin
from database.config import Base
from .role_permissions import role_permissions


class Role(TimestampMixin, Base):
    __tablename__ = "roles"
    role_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name = Column(String(50), unique=True, nullable=False)

    employees = relationship("Employee", back_populates="role")
    permissions = relationship("Permission", secondary=role_permissions,
                               back_populates="roles")

    def __repr__(self):
        return f"<Role (name: {self.name})>"
