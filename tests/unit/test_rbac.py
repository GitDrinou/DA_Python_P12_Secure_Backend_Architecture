from sqlalchemy import select
from database.models import Role, Permission
from security.rbac import seed_rbac
from security.permissions import (
    ROLE_MANAGEMENT,
    ROLE_SALES,
    ROLE_SUPPORT,
    ALL_PERMISSIONS,
    ROLE_PERMISSION_MAPPER, PERM_CUSTOMERS_READ_ALL, PERM_CONTRACTS_READ_ALL,
    PERM_EVENTS_READ_ALL, PERM_EMPLOYEES_READ_ALL, PERM_EMPLOYEES_CREATE,
    ROLE_ADMIN
)


def test_seed_rbac_creates_all_roles(db_session):
    roles = seed_rbac(db_session)

    assert ROLE_ADMIN in roles
    assert ROLE_MANAGEMENT in roles
    assert ROLE_SALES in roles
    assert ROLE_SUPPORT in roles


def test_seed_rbac_creates_roles_and_permissions(db_session):
    seed_rbac(db_session)

    roles = db_session.execute(select(Role)).scalars().all()
    permissions = db_session.execute(select(Permission)).scalars().all()

    role_names = {role.name for role in roles}
    permission_codes = {permission.code for permission in permissions}

    assert role_names == {
        ROLE_ADMIN,
        ROLE_MANAGEMENT,
        ROLE_SALES,
        ROLE_SUPPORT
    }
    assert permission_codes == set(ALL_PERMISSIONS.keys())


def test_seed_rbac_populates_role_permissions(db_session):
    seed_rbac(db_session)

    roles = {
        role.name: role
        for role in db_session.execute(select(Role)).scalars().all()
    }

    for role_name, expected_codes in ROLE_PERMISSION_MAPPER.items():
        actual_codes = {
            permission.code for permission in roles[role_name].permissions
        }
        assert actual_codes == expected_codes


def test_seed_rbac_is_idempotent(db_session):
    seed_rbac(db_session)

    roles = db_session.execute(select(Role)).scalars().all()
    permissions = db_session.execute(select(Permission)).scalars().all()

    assert len(roles) == 4
    assert len(permissions) == len(ALL_PERMISSIONS)


def test_management_role_contains_expected_permissions(db_session):
    roles = seed_rbac(db_session)
    management_role = roles[ROLE_MANAGEMENT]

    codes = {permission.code for permission in management_role.permissions}

    assert PERM_CUSTOMERS_READ_ALL in codes
    assert PERM_CONTRACTS_READ_ALL in codes
    assert PERM_EVENTS_READ_ALL in codes
    assert PERM_EMPLOYEES_READ_ALL in codes
    assert PERM_EMPLOYEES_CREATE in codes
