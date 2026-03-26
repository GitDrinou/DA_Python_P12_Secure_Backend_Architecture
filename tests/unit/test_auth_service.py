import pytest
from security.auth_service import login, AuthenticationError
from security.jwt_handler import decode_token


def test_login_returns_tokens_and_role(db_session, employee_with_password):
    employee = employee_with_password["employee"]
    plain_password = employee_with_password["plain_password"]

    result = login(db_session, employee.email, plain_password)

    assert "access_token" in result
    assert "refresh_token" in result
    assert result["employee_id"] == employee.employee_id
    assert result["role"] == "commercial"


def test_login_rejects_unknown_email(db_session):
    with pytest.raises(AuthenticationError, match="Invalid email or password"):
        login(db_session, "unknown@example.com", "secret")


def test_login_rejects_inactive_user(
        db_session,
        inactive_employee_with_password
):
    employee = inactive_employee_with_password["employee"]
    plain_password = inactive_employee_with_password["plain_password"]

    with pytest.raises(AuthenticationError, match="Employee is not active"):
        login(db_session, employee.email, plain_password)


def test_login_rejects_invalid_password(db_session, employee_with_password):
    employee = employee_with_password["employee"]

    with pytest.raises(AuthenticationError, match="Invalid password"):
        login(db_session, employee.email, "bad-password")


def test_login_returns_valid_access_token_payload(
        db_session,
        employee_with_password
):
    employee = employee_with_password["employee"]
    plain_password = employee_with_password["plain_password"]

    result = login(db_session, employee.email, plain_password)
    payload = decode_token(result["access_token"])

    assert payload["sub"] == employee.employee_id
    assert payload["email"] == employee.email
    assert payload["role"] == employee.role.name
    assert payload["type"] == "access"
    assert payload["iss"] == "epic-events-crm-test"
    assert "iat" in payload
    assert "exp" in payload
    assert "jti" in payload


def test_login_returns_different_access_and_refresh_tokens(
    db_session,
    employee_with_password,
):
    employee = employee_with_password["employee"]
    plain_password = employee_with_password["plain_password"]

    result = login(db_session, employee.email, plain_password)

    assert result["access_token"] != result["refresh_token"]

    access_payload = decode_token(result["access_token"])
    refresh_payload = decode_token(result["refresh_token"])

    assert access_payload["type"] == "access"
    assert refresh_payload["type"] == "refresh"
    assert access_payload["jti"] != refresh_payload["jti"]
