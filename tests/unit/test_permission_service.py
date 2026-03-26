import pytest
from security.permissions import (
    ROLE_MANAGEMENT,
    ROLE_SUPPORT,
    PERM_PERMISSIONS_CREATE,
)
from security.rbac import seed_rbac
from services.permission_service import PermissionService


def test_list_permissions_returns_ordered_permissions(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    permissions = service.list_permissions()

    assert len(permissions) > 0
    codes = [permission.code for permission in permissions]
    assert codes == sorted(codes)


def test_get_permission(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    permission = service.get_permission(PERM_PERMISSIONS_CREATE)

    assert permission.code == PERM_PERMISSIONS_CREATE


def test_get_permission_raises_when_missing(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    with pytest.raises(ValueError, match="Permission not found"):
        service.get_permission("missing.permission")


def test_creates_permission(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    permission = service.create_permission(
        code="test.code",
        description="description test permission",
    )

    assert permission.code == "test.code"
    assert permission.description == "description test permission"


def test_create_permission_rejects_missing_code(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    with pytest.raises(ValueError, match="Permission code is required"):
        service.create_permission(
            code="",
            description="description test permission",
        )


def test_create_permission_rejects_duplicate_code(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    service.create_permission(
        code="test.code",
        description="description test permission",
    )

    with pytest.raises(ValueError, match="Permission already exists"):
        service.create_permission(
            code="test.code",
            description="Duplicate",
        )


def test_update_permission_updates_code_and_description(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    service.create_permission(
        code="test.code",
        description="description test permission",
    )

    permission = service.update_permission(
        permission_code="test.code",
        new_code="test.new_code",
        description="description test permission",
    )

    assert permission.code == "test.new_code"
    assert permission.description == "description test permission"


def test_update_permission_rejects_duplicate_new_code(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    service.create_permission("test.code", "test description code")
    service.create_permission("test.new_code", "test description new code")

    with pytest.raises(ValueError, match="Permission already exists"):
        service.update_permission(
            permission_code="test.code",
            new_code="test.new_code",
        )


def test_delete_permission_removes_permission(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    service.create_permission(
        code="test.code",
        description="description test permission",
    )
    result = service.delete_permission("test.code")
    assert result is True

    with pytest.raises(ValueError, match="Permission not found"):
        service.get_permission("test.code")


def test_list_roles_returns_roles_with_permissions(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    roles = service.list_roles()

    assert len(roles) >= 3
    role_names = [role.name for role in roles]
    assert role_names == sorted(role_names)

    for role in roles:
        assert isinstance(role.permissions, list)


def test_get_role_returns_existing_role(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    role = service.get_role(ROLE_MANAGEMENT)

    assert role.name == ROLE_MANAGEMENT
    assert len(role.permissions) > 0


def test_get_role_raises_when_missing(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    with pytest.raises(ValueError, match="Role not found"):
        service.get_role("unknown-role")


def test_assign_permission_to_role_adds_permission(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    service.create_permission(
        code="test.code",
        description="description test permission",
    )

    role = service.assign_permission_to_role(
        role_name=ROLE_SUPPORT,
        permission_code="test.code",
    )

    codes = {permission.code for permission in role.permissions}
    assert "test.code" in codes


def test_remove_permission_from_role_removes_permission(db_session):
    seed_rbac(db_session)
    service = PermissionService(db_session)

    service.create_permission(
        code="test.code",
        description="description test permission",
    )
    service.assign_permission_to_role(
        role_name=ROLE_SUPPORT,
        permission_code="test.code",
    )

    role = service.remove_permission_from_role(
        role_name=ROLE_SUPPORT,
        permission_code="test.code",
    )

    codes = {permission.code for permission in role.permissions}
    assert "test.code" not in codes
