from sqlalchemy.orm import joinedload

from database.models import Employee
from security.jwt_handler import create_access_token, create_refresh_token
from security.passwords import verify_password


class AuthenticationError(Exception):
    pass


def login(db, email, plain_password):
    employee = (
        db.query(Employee)
        .options(joinedload(Employee.role))
        .filter(Employee.email == email)
        .first()
    )

    if employee is None:
        raise AuthenticationError("Invalid email or password")

    if not employee.is_active:
        raise AuthenticationError("User is not active")

    if not verify_password(employee.password_hash, plain_password):
        raise AuthenticationError("Invalid password")

    access_token = create_access_token(employee)
    refresh_token = create_refresh_token(employee)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "employee_id": employee.employee_id,
        "role": employee.role.name if employee.role else None,
    }
