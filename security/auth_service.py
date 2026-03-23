from sqlalchemy.orm import joinedload
from database.models import Employee, Role
from security.jwt_handler import create_access_token, create_refresh_token
from security.passwords import verify_password


class AuthenticationError(Exception):
    pass


def login(db, email, plain_password):
    employee = (
        db.query(Employee)
        .options(joinedload(Employee.role).joinedload(Role.permissions))
        .filter_by(email=email)
        .first()
    )

    if employee is None:
        raise AuthenticationError("Invalid email or password")

    if not employee.is_active:
        raise AuthenticationError("Employee is not active")

    if not verify_password(plain_password, employee.password_hash):
        raise AuthenticationError("Invalid password")

    access_token = create_access_token(employee)
    refresh_token = create_refresh_token(employee)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "employee_id": employee.employee_id,
        "role": employee.role.name if employee.role else None,
    }
