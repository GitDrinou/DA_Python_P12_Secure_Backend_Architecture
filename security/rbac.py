from sqlalchemy import select
from sqlalchemy.orm import joinedload
from database.models import Role, Permission
from security.permissions import ROLES, ALL_PERMISSIONS, ROLE_PERMISSION_MAPPER


def seed_rbac(session):
    roles_by_name = {
        role.name: role
        for role in session.execute(
            select(Role).options(joinedload(Role.permissions))
        ).scalars().unique().all()
    }

    for role_name in ROLES:
        if role_name not in roles_by_name:
            role = Role(name=role_name)
            session.add(role)
            session.flush()
            roles_by_name[role_name] = role

    permissions_by_code = {
        permission.code: permission
        for permission in session.execute(select(Permission)).scalars().all()
    }

    for code, description in ALL_PERMISSIONS.items():
        if code not in permissions_by_code:
            permission = Permission(code=code, description=description)
            session.add(permission)
            session.flush()
            permissions_by_code[code] = permission

    session.flush()

    roles_by_name = {
        role.name: role
        for role in session.execute(
            select(Role).options(joinedload(Role.permissions))
        ).scalars().unique().all()
    }

    for role_name, permission_codes in ROLE_PERMISSION_MAPPER.items():
        role = roles_by_name[role_name]
        current_codes = {permission.code for permission in role.permissions}

        missing_codes = set(permission_codes) - current_codes
        extra_codes = current_codes - set(permission_codes)

        for code in missing_codes:
            role.permissions.append(permissions_by_code[code])

        if extra_codes:
            role.permissions = [
                permission
                for permission in role.permissions
                if permission.code not in extra_codes
            ]

    session.commit()

    return {
        role.name: role
        for role in session.execute(
            select(Role).options(joinedload(Role.permissions))
        ).scalars().unique().all()
    }
