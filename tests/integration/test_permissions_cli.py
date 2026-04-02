from cli.commands import permissions
from click.testing import CliRunner
from security.rbac import seed_rbac
from click.core import Command
from typing import cast
from security.session_store import save_session
from security.jwt_handler import create_access_token, create_refresh_token
from tests.factories import create_employee


def login_employee(employee):
    save_session(create_access_token(employee), create_refresh_token(employee))


def test_permissions_list_allows_admin(monkeypatch, db_session, tmp_path):
    from security import session_store

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)
    admin = create_employee(
        db_session=db_session,
        role_name="admin",
        full_name="Admin Permissions",
        email="admin.permissions@test.com",
        password="Password123!",
    )
    login_employee(admin)

    runner = CliRunner()
    result = runner.invoke(
        cast(Command, permissions.cli),
        ["list"],
        obj={"db_session": db_session},
    )

    assert result.exit_code == 0
    assert "Permissions" in result.output
    assert "code" in result.output


def test_permissions_create_uses_prompts(monkeypatch, db_session, tmp_path):
    from security import session_store
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
        role_name="admin",
        full_name="Admin Create",
        email="admin.create@test.com",
        password="Password123!",
    )
    login_employee(admin)

    runner = CliRunner()
    result = runner.invoke(
        cast(Command, permissions.cli),
        ["create"],
        input="reports.export\nExporter les rapports\n",
        obj={"db_session": db_session},
    )

    service = PermissionService(db_session)
    created = service.get_permission("reports.export")

    assert result.exit_code == 0
    assert "Permission created: reports.export" in result.output
    assert created.code == "reports.export"
