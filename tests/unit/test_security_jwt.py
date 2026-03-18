import jwt
import pytest
from datetime import datetime, timezone, timedelta
from security import jwt_handler
from security.jwt_handler import create_access_token, decode_token, \
    create_refresh_token, refresh_access_token, TokenExpiredError, TokenError


def test_create_access_token_return_string(sales_employee):
    token = create_access_token(sales_employee)

    assert isinstance(token, str)
    assert token.count(".") == 2


def test_create_access_token_contains_expected_claims(sales_employee):
    token = create_access_token(sales_employee)
    payload = decode_token(token)

    assert payload["sub"] == sales_employee.employee_id
    assert payload["email"] == sales_employee.email
    assert payload["role"] == sales_employee.role.name
    assert payload["type"] == "access"
    assert payload["iss"] == "epic-events-crm-test"
    assert "iat" in payload
    assert "exp" in payload
    assert "jti" in payload


def test_access_and_refresh_tokens_have_different_jti(sales_employee):
    access_token = create_access_token(sales_employee)
    refresh_token = create_refresh_token(sales_employee)

    access_payload = decode_token(access_token)
    refresh_payload = decode_token(refresh_token)

    assert access_payload["jti"] != refresh_payload["jti"]


def test_decode_valid_token(sales_employee):
    token = create_access_token(sales_employee)
    payload = decode_token(token)

    assert payload["sub"] == sales_employee.employee_id
    assert payload["type"] == "access"


def test_refresh_token_returns_new_access_token(sales_employee):
    refresh_token = create_refresh_token(sales_employee)
    new_access_token = refresh_access_token(refresh_token, sales_employee)
    payload = decode_token(new_access_token)

    assert isinstance(new_access_token, str)
    assert payload["sub"] == sales_employee.employee_id
    assert payload["type"] == "access"


def test_decode_expired_token(sales_employee):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sales_employee.employee_id,
        "email": sales_employee.email,
        "role": sales_employee.role.name,
        "type": "access",
        "iss": jwt_handler.JWT_ISSUER,
        "iat": now - timedelta(minutes=2),
        "exp": now - timedelta(minutes=1),
        "jti": "expired-token-id",
    }

    token = jwt.encode(
        payload,
        jwt_handler.JWT_SECRET_KEY,
        algorithm=jwt_handler.JWT_ALGORITHM,
    )

    with pytest.raises(TokenExpiredError, match="Token expired"):
        decode_token(token)


def test_refresh_token_rejects_access_token(sales_employee):
    access_token = create_access_token(sales_employee)

    with pytest.raises(TokenError, match="Given token is not a refresh token"):
        refresh_access_token(access_token, sales_employee)


def test_refresh_token_rejects_other_employee(sales_employee,
                                              support_employee):
    refresh_token = create_refresh_token(sales_employee)

    with pytest.raises(TokenError, match="Refresh token does not belong to "
                                         "this employee"):
        refresh_access_token(refresh_token, support_employee)
