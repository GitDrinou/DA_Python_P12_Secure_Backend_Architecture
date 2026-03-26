import sys
from security.session_store import load_session
from security.rbac import seed_rbac
from tests.factories import create_employee


def test_epic_events_login_success_saves_session(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json",
    )

    seed_rbac(db_session)
    employee = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Alice Martin",
        email="alice.login@test.com",
        password="Password123!",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "epic_events.py",
            "login",
            "--email",
            employee.email,
            "--password",
            "Password123!",
        ],
    )

    exit_code = epic_events.main(db_session=db_session)
    output = capsys.readouterr().out

    saved_session = load_session()

    assert exit_code == 0
    assert "[SUCCESS] Successfully logged in" in output
    assert saved_session is not None
    assert "access_token" in saved_session
    assert "refresh_token" in saved_session


def test_epic_events_login_rejects_invalid_password(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json",
    )

    seed_rbac(db_session)

    employee = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Alice Martin",
        email="alice.invalid-password@test.com",
        password="Password123!",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "epic_events.py",
            "login",
            "--email",
            employee.email,
            "--password",
            "WrongPassword!",
        ],
    )

    exit_code = epic_events.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "[AUTH] Invalid password" in output


def test_epic_events_login_rejects_unknown_email(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json",
    )

    seed_rbac(db_session)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "epic_events.py",
            "login",
            "--email",
            "missing@test.com",
            "--password",
            "Password123!",
        ],
    )

    exit_code = epic_events.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "[AUTH] Invalid email or password" in output


def test_epic_events_login_rejects_inactive_employee(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json",
    )

    seed_rbac(db_session)

    employee = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Inactive User",
        email="inactive.login@test.com",
        password="Password123!",
        is_active=False,
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "epic_events.py",
            "login",
            "--email",
            employee.email,
            "--password",
            "Password123!",
        ],
    )

    exit_code = epic_events.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "[AUTH] Employee is not active" in output


def test_epic_events_whoami_after_login(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json",
    )

    seed_rbac(db_session)
    employee = create_employee(
        db_session=db_session,
        role_name="gestion",
        full_name="Admin Test",
        email="admin.whoami@test.com",
        password="Password123!",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "epic_events.py",
            "login",
            "--email",
            employee.email,
            "--password",
            "Password123!",
        ],
    )
    login_exit_code = epic_events.main(db_session=db_session)
    login_output = capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["epic_events.py", "whoami"])
    whoami_exit_code = epic_events.main(db_session=db_session)
    whoami_output = capsys.readouterr().out

    assert login_exit_code == 0
    assert "[SUCCESS] Successfully logged in" in login_output

    assert whoami_exit_code == 0
    assert "[INFO] Connected user" in whoami_output
    assert f"id: {employee.employee_id}" in whoami_output
    assert f"name: {employee.full_name}" in whoami_output
    assert f"email: {employee.email}" in whoami_output
    assert "role: gestion" in whoami_output
