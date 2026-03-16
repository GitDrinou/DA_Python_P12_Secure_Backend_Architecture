import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from database.config import Base
from .base import TimestampMixin
from .role_permissions import role_permissions


class Permission(TimestampMixin, Base):
    __tablename__ = "permissions"

    permission_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    code = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions"
    )

    def __repr__(self):
        return f"<Permission (code: {self.code})>"
