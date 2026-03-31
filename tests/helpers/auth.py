from security.jwt_handler import create_access_token, create_refresh_token
from security.rbac import seed_rbac
from security.session_store import save_session
from tests.factories import create_employee


def _prepare_session_store(monkeypatch, tmp_path):
    from security import session_store

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )


def login_employee(employee):
    save_session(
        create_access_token(employee),
        create_refresh_token(employee),
    )
    return employee


def login_as_manager(monkeypatch, db_session, tmp_path):
    _prepare_session_store(monkeypatch, tmp_path)
    seed_rbac(db_session)

    manager = create_employee(
        db_session=db_session,
        role_name="gestion",
        full_name="Manager Test",
        email="manager.contracts@test.com",
        password="Password123!",
    )
    return login_employee(manager)


def login_as_sales(monkeypatch, db_session, tmp_path):
    _prepare_session_store(monkeypatch, tmp_path)
    seed_rbac(db_session)

    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales Test",
        email="sales.contracts@test.com",
        password="Password123!",
    )
    return login_employee(sales)


def login_as_support(monkeypatch, db_session, tmp_path):
    _prepare_session_store(monkeypatch, tmp_path)
    seed_rbac(db_session)

    support = create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Support Test",
        email="support.contracts@test.com",
        password="Password123!",
    )
    return login_employee(support)
