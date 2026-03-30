import sys

from security.permissions import ROLE_ADMIN, ROLE_SALES
from security.rbac import seed_rbac
from security.session_store import save_session
from security.jwt_handler import create_access_token, create_refresh_token
from tests.factories import create_employee


def login_employee_for_cli(employee):
    access_token = create_access_token(employee)
    refresh_token = create_refresh_token(employee)
    save_session(access_token, refresh_token)


def test_permissions_list_allows_management(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    from security import session_store
    import permissions

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)

    admin = create_employee(
        db_session=db_session,
        role_name=ROLE_ADMIN,
        full_name="Admin Permissions",
        email="admin@test.com",
        password="Password123!",
    )
    login_employee_for_cli(admin)

    monkeypatch.setattr(sys, "argv", ["permissions.py", "list"])

    exit_code = permissions.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "code:" in output
    assert "description:" in output


def test_permissions_list_rejects_sales(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    from security import session_store
    import permissions

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)

    sales = create_employee(
        db_session=db_session,
        role_name=ROLE_SALES,
        full_name="Sales Permissions",
        email="sales@test.com",
        password="Password123!",
    )
    login_employee_for_cli(sales)

    monkeypatch.setattr(sys, "argv", ["permissions.py", "list"])

    exit_code = permissions.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "[UNEXPECTED] You don't have permission" in output


def test_permissions_create_allows_management(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    from security import session_store
    import permissions
    from services.permission_service import PermissionService

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)

    admin = create_employee(
        db_session=db_session,
        role_name=ROLE_ADMIN,
        full_name="Admin Create Permission",
        email="admin@test.com",
        password="Password123!",
    )
    login_employee_for_cli(admin)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "permissions.py",
            "create",
            "--code",
            "test.code",
            "--description",
            "description test permission",
        ],
    )

    exit_code = permissions.main(db_session=db_session)
    output = capsys.readouterr().out

    service = PermissionService(db_session)
    created = service.get_permission("test.code")

    assert exit_code == 0
    assert "[SUCCESS] Permission created: test.code" in output
    assert created.code == "test.code"


def test_permissions_update_allows_management(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    from security import session_store
    import permissions
    from services.permission_service import PermissionService

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)
    service = PermissionService(db_session)
    service.create_permission("test.code", "description test permission")

    admin = create_employee(
        db_session=db_session,
        role_name=ROLE_ADMIN,
        full_name="Admin Update Permission",
        email="admin@test.com",
        password="Password123!",
    )
    login_employee_for_cli(admin)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "permissions.py",
            "update",
            "--code",
            "test.code",
            "--new-code",
            "test.new_code",
            "--description",
            "new description test permission",
        ],
    )

    exit_code = permissions.main(db_session=db_session)
    output = capsys.readouterr().out

    updated = service.get_permission("test.new_code")

    assert exit_code == 0
    assert "[SUCCESS] Permission updated: test.new_code" in output
    assert updated.description == "new description test permission"


def test_permissions_delete_allows_management(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    from security import session_store
    import permissions
    from services.permission_service import PermissionService

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)
    service = PermissionService(db_session)
    service.create_permission("test.code", "description test permission")

    admin = create_employee(
        db_session=db_session,
        role_name=ROLE_ADMIN,
        full_name="Admin Delete Permission",
        email="admin@test.com",
        password="Password123!",
    )
    login_employee_for_cli(admin)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "permissions.py",
            "delete",
            "--code",
            "test.code",
        ],
    )

    exit_code = permissions.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "[SUCCESS] Permission deleted" in output


def test_permissions_lists_roles(monkeypatch, db_session, tmp_path, capsys):
    from security import session_store
    import permissions

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)

    admin = create_employee(
        db_session=db_session,
        role_name=ROLE_ADMIN,
        full_name="Admin Roles Permission",
        email="admin@test.com",
        password="Password123!",
    )
    login_employee_for_cli(admin)

    monkeypatch.setattr(sys, "argv", ["permissions.py", "roles"])

    exit_code = permissions.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "role: commercial" in output
    assert "role: gestion" in output
    assert "role: support" in output


def test_permissions_assign_allows_management(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    from security import session_store
    import permissions
    from services.permission_service import PermissionService

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)
    service = PermissionService(db_session)
    service.create_permission("test.code", "description test permission")

    admin = create_employee(
        db_session=db_session,
        role_name=ROLE_ADMIN,
        full_name="Admin Assign Permission",
        email="admin@test.com",
        password="Password123!",
    )
    login_employee_for_cli(admin)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "permissions.py",
            "assign",
            "--role",
            "support",
            "--code",
            "test.code",
        ],
    )

    exit_code = permissions.main(db_session=db_session)
    output = capsys.readouterr().out

    role = service.get_role("support")
    codes = {permission.code for permission in role.permissions}

    assert exit_code == 0
    assert ("[SUCCESS] Permission test.code assigned to role support" in
            output)
    assert "test.code" in codes


def test_permissions_remove_allows_management(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    from security import session_store
    import permissions
    from services.permission_service import PermissionService

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)
    service = PermissionService(db_session)
    service.create_permission("test.code", "description test permission")
    service.assign_permission_to_role("support", "test.code")

    admin = create_employee(
        db_session=db_session,
        role_name=ROLE_ADMIN,
        full_name="Admin Remove Permission",
        email="admin@test.com",
        password="Password123!",
    )
    login_employee_for_cli(admin)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "permissions.py",
            "remove",
            "--role",
            "support",
            "--code",
            "test.code",
        ],
    )

    exit_code = permissions.main(db_session=db_session)
    output = capsys.readouterr().out

    role = service.get_role("support")
    codes = {permission.code for permission in role.permissions}

    assert exit_code == 0
    assert ("[SUCCESS] Permission test.code removed from role support" in
            output)
    assert "test.code" not in codes
