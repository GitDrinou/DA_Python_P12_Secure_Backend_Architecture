from sqlalchemy import Table, Column, ForeignKey, String
from database.config import Base


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        String(36),
        ForeignKey("roles.role_id"),
        primary_key=True),
    Column(
        "permission_id",
        String(36),
        ForeignKey("permissions.permission_id"),
        primary_key=True),
)
