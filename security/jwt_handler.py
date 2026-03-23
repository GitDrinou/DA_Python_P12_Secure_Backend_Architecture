import uuid
import jwt
from datetime import datetime, timezone, timedelta
from jwt import ExpiredSignatureError, InvalidTokenError
from core.settings import get_settings


JWT_SETTINGS = get_settings().jwt
JWT_SECRET_KEY = JWT_SETTINGS.secret_key
JWT_ALGORITHM = JWT_SETTINGS.algorithm
JWT_ISSUER = JWT_SETTINGS.issuer
ACCESS_TOKEN_EXPIRE_MINUTES = JWT_SETTINGS.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = JWT_SETTINGS.refresh_token_expire_days


class TokenError(Exception):
    pass


class TokenExpiredError(TokenError):
    pass


def _build_payload(employee, token_type, expires_delta):
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": str(employee.employee_id),
        "email": employee.email,
        "role": employee.role.name if employee.role else None,
        "type": token_type,
        "iss": JWT_ISSUER,
        "iat": now,
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    return payload


def create_access_token(employee):
    payload = _build_payload(
        employee=employee,
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(employee):
    payload = _build_payload(
        employee=employee,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            options={
                "require": ["sub", "type", "iss", "iat", "exp", "jti"],
            },
        )
        return payload
    except ExpiredSignatureError as exc:
        raise TokenExpiredError("Token expired") from exc
    except InvalidTokenError as exc:
        raise TokenError("Invalid token") from exc


def refresh_access_token(refresh_token, employee):
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise TokenError("Given token is not a refresh token")

    if payload.get("sub") != employee.employee_id:
        raise TokenError("Refresh token does not belong to this employee")

    return create_access_token(employee)
