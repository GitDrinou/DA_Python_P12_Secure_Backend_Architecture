from security.session_store import load_session
from cli.auth_cli import authenticate_employee


def test_authenticate_employee_returns_authenticaded_employee(
        db_session,
        employee_with_password,
        monkeypatch,
        tmp_path
):
    from security import session_store

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    employee = employee_with_password["employee"]
    plain_password = employee_with_password["plain_password"]

    authenticated_employee = authenticate_employee(
        db_session,
        employee.email,
        plain_password
    )

    saved_session = load_session()

    assert authenticated_employee.employee_id == employee.employee_id
    assert authenticated_employee.role.name == "commercial"
    assert saved_session is not None
    assert "access_token" in saved_session
    assert "refresh_token" in saved_session

