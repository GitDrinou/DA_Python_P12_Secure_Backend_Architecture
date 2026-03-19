from database.models import Role, Permission
from sqlalchemy import select


COMMON_PERMISSIONS = {
    "customers.read_all": "Lire tous les clients",
    "contracts.read_all": "Lire tous les contrats",
    "events.read_all": "Lire tous les événements",
}

MANAGEMENT_PERMISSIONS = {
    "employees.read_all": "Lire tous les collaborateurs",
    "employees.create": "Créer un collaborateur",
    "employees.update": "Mettre à jour un collaborateur",
    "employees.delete": "Supprimer un collaborateur",
    "contracts.create_all": "Créer tous les contrats",
    "contracts.update_all": "Modifier tous les contrats",
    "events.filter_without_support": (
        "Filtrer les événements sans contact support"),
    "events.assign_support": "Assigner un contact support à un événement",
}

SALES_PERMISSIONS = {
    "customers.create_owned": (
        "Créer un client rattaché au commercial connecté"),
    "customers.update_owned": "Modifier ses propres clients",
    "contracts.update_owned_customers": (
        "Modifier les contrats dont le commercial est responsable"),
    "contracts.filter_unsigned_or_unpaid": (
        "Filtrer les contrats non signés ou non totalement payés"),
    "events.create_for_signed_contract_owned_customers": (
        "Créer un événement pour un contrat signé par un client du commercial"
    ),
}

SUPPORT_PERMISSIONS = {
    "events.filter_assigned_to_me": (
        "Filtrer les événements attribué au support connecté"),
    "events.update_assigned": (
        "Modifier les événements attribués au support connecté"),
}

ALL_PERMISSIONS = {
    **COMMON_PERMISSIONS,
    **MANAGEMENT_PERMISSIONS,
    **SALES_PERMISSIONS,
    **SUPPORT_PERMISSIONS,
}

ROLE_PERMISSION_MAPPER = {
    "gestion": set(COMMON_PERMISSIONS) | set(MANAGEMENT_PERMISSIONS),
    "commercial": set(COMMON_PERMISSIONS) | set(SALES_PERMISSIONS),
    "support": set(COMMON_PERMISSIONS) | set(SUPPORT_PERMISSIONS),
}


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


def get_role_permission_codes(role_name):
    return ROLE_PERMISSION_MAPPER.get(role_name, set())
