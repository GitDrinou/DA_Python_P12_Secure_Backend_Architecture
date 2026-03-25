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
        tmp_path / "session.json",
    )

    seed_rbac(db_session)
    manager = create_employee(
        db_session=db_session,
        role_name="gestion",
        full_name="Manager Test",
        email="manager.contracts@test.com",
        password="Password123!",
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


def login_as_sales(monkeypatch, db_session, tmp_path):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json",
    )

    seed_rbac(db_session)
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales Test",
        email="sales.contracts@test.com",
        password="Password123!",
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


def login_as_support(monkeypatch, db_session, tmp_path):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json",
    )

    seed_rbac(db_session)
    support = create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Support Test",
        email="support.contracts@test.com",
        password="Password123!",
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
            support.email,
            "--password",
            "Password123!",
        ],
    )
    epic_events.main(db_session=db_session)
    return support
