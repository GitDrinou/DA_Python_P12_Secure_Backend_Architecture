import sys
from security.rbac import seed_rbac
from tests.factories import create_employee


def login_as_manager(monkeypatch, db_session, tmp_path):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)
    manager = create_employee(
        db_session=db_session,
        role_name="gestion",
        full_name="Manager Test",
        email="manager@mail.com",
        password="Password123!"
    )
    db_session.flush()
    db_session.commit()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "epic_events.py",
            "login",
            "--email",
            manager.email,
            "--password",
            "Password123!",
        ],
    )
    epic_events.main(db_session=db_session)
    return manager


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
    assert ("[FORBIDDEN] No active session."
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

    print(output)

    assert exit_code == 0
    assert "[SUCCESS] Employee created" in output
