from database.models import Role, Permission
from sqlalchemy import select
from security.permissions import ALL_PERMISSIONS, ROLE_PERMISSION_MAPPER


def seed_rbac(session):
    """ Seed roles, permissions and relation role_permission."""
    existing_roles = {
        role.name: role
        for role in session.execute(select(Role)).scalars().all()
    }

    existing_permissions = {
        permission.code: permission
        for permission in session.execute(select(Permission)).scalars().all()
    }

    for code, description in ALL_PERMISSIONS.items():
        if code not in existing_permissions:
            permission = Permission(code=code, description=description)
            session.add(permission)
            existing_permissions[code] = permission

    session.flush()

    for role_name in ROLE_PERMISSION_MAPPER:
        if role_name not in existing_roles:
            role = Role(name=role_name)
            session.add(role)
            existing_roles[role_name] = role

    session.flush()

    for role_name, permission_codes in ROLE_PERMISSION_MAPPER.items():
        role = existing_roles[role_name]
        role.permissions = [
            existing_permissions[code]
            for code in sorted(permission_codes)
        ]

    session.commit()
    return existing_roles
