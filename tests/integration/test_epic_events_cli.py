from click.testing import CliRunner
from security.rbac import seed_rbac
from tests.factories import create_employee
from typing import cast
from click.core import Command


def test_login_success_with_click_prompts(monkeypatch, db_session, tmp_path):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)

    create_employee(
        db_session=db_session,
        role_name="admin",
        full_name="Admin Test",
        email="admin@test.com",
        password="Password123!",
    )

    runner = CliRunner()
    result = runner.invoke(
        cast(Command, epic_events.cli),
        ["login"],
        input="admin@test.com\nPassword123!\n",
        obj={"db_session": db_session},
    )

    assert result.exit_code == 0
    assert "Successfully logged in" in result.output


def test_whoami_displays_current_user(monkeypatch, db_session, tmp_path):
    from security import session_store
    from security.session_store import save_session
    from security.jwt_handler import create_access_token, create_refresh_token
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)
    employee = create_employee(
        db_session=db_session,
        role_name="admin",
        full_name="Admin WhoAmI",
        email="whoami@test.com",
        password="Password123!",
    )

    save_session(
        create_access_token(employee),
        create_refresh_token(employee)
    )

    runner = CliRunner()
    result = runner.invoke(
        cast(Command, epic_events.cli),
        ["whoami"],
        obj={"db_session": db_session},
    )

    assert result.exit_code == 0
    assert "Connected user" in result.output
    assert "Admin WhoAmI" in result.output
    assert "admin" in result.output
