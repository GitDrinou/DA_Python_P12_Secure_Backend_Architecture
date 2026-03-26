from security.passwords import verify_password
from security.rbac import seed_rbac
from security.session_store import load_session
from tests.factories import create_employee


def test_login_command_saves_session(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    from security import session_store
    import sys
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
        role_name="commercial",
        full_name="Alice Martin",
        email="sales@mail.com",
        password="Password123!"
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

    print(output)

    assert verify_password("Password123!", employee.password_hash) is True
    assert exit_code == 0
    assert "[SUCCESS] Successfully logged in" in output
    assert load_session() is not None


def test_logout_command_clears_session(monkeypatch, tmp_path, capsys):
    from security import session_store
    import sys
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    session_store.save_session("access", "refresh")

    monkeypatch.setattr(sys, "argv", ["epic_events.py", "logout"])

    exit_code = epic_events.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "[SUCCESS] Successfully logged out" in output
    assert load_session() is None
