import sys
from tests.helpers.auth import login_as_manager


def test_employees_list_requires_login(monkeypatch, capsys, tmp_path):
    from security import session_store
    import employees

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )
    monkeypatch.setattr(sys, "argv", ["employees.py", "list"])

    exit_code = employees.main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert ("[FORBIDDEN] No active session. "
            "Please login with: >> epic_events.py login <<") in output


def test_employees_create_as_manager(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import employees

    login_as_manager(monkeypatch, db_session, tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "employees.py",
            "create",
            "--full-name", "New Employee",
            "--email", "new.employee@test.com",
            "--password", "Password123!",
            "--role", "support",
        ],
    )

    exit_code = employees.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "[SUCCESS] Employee created" in output
