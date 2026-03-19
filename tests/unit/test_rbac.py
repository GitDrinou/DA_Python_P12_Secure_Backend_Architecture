from sqlalchemy import select
from database.models import Role, Permission
from security.rbac import seed_rbac, ALL_PERMISSIONS, ROLE_PERMISSION_MAPPER


def test_seed_rbac_creates_roles_and_permissions(db_session):
    seed_rbac(db_session)

    roles = db_session.execute(select(Role)).scalars().all()
    permissions = db_session.execute(select(Permission)).scalars().all()

    role_names = {role.name for role in roles}
    permission_codes = {permission.code for permission in permissions}

    assert role_names == {"gestion", "commercial", "support"}
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
    seed_rbac(db_session)

    roles = db_session.execute(select(Role)).scalars().all()
    permissions = db_session.execute(select(Permission)).scalars().all()

    assert len(roles) == 3
    assert len(permissions) == len(ALL_PERMISSIONS)
