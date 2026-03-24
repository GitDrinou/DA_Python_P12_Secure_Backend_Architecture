import sys
from security.rbac import seed_rbac
from tests.factories import create_employee


def login_as_sales(monkeypatch, db_session, tmp_path):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    seed_rbac(db_session)
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Commercial Test",
        email="sales@mail.com",
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
            sales.email,
            "--password",
            "Password123!",
        ],
    )
    epic_events.main(db_session=db_session)
    return sales


def test_customers_list_requires_login(monkeypatch, capsys, tmp_path):
    from security import session_store
    import customers

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )
    monkeypatch.setattr(sys, "argv", ["customers.py", "list"])

    exit_code = customers.main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert ("[FORBIDDEN] No active session. "
            "Please login with: >> epic_events.py login <<") in output


def test_customers_create_as_sales(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import customers

    sales = login_as_sales(monkeypatch, db_session, tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "customers.py",
            "create",
            "--full-name", "New Customer",
            "--email", "new.customer@test.com",
            "--phone", "123-456-789",
            "--company-name", "Customer Test SA",
            "--sales-id", sales.employee_id,
        ],
    )

    exit_code = customers.main(db_session=db_session)
    output = capsys.readouterr().out

    print(output)

    assert exit_code == 0
    assert "[SUCCESS] Customer created" in output
