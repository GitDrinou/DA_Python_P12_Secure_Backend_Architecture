from sqlalchemy.orm import joinedload

from database.models import Employee, Role
from security.jwt_handler import decode_token


class AuthorizationError(Exception):
    pass


def get_authenticated_employee(db_session, token):
    payload = decode_token(token)

    employee = (
        db_session.query(Employee)
        .options(joinedload(Employee.role).joinedload(Role.permissions))
        .filter(Employee.employee_id == payload["sub"])
        .first()
    )

    if employee is None:
        raise AuthorizationError("Unknown employee")

    if not employee.is_active:
        raise AuthorizationError("Inactive user")

    return employee


def has_permission(employee, permission_code):
    if employee is None or employee.role is None:
        return False

    return any(
        permission.code == permission_code
        for permission in employee.role.permissions
    )


def require_permission(employee, permission_code):
    if not has_permission(employee, permission_code):
        raise AuthorizationError(f"Missing permission {permission_code}")

    return None


def can_update_customer(employee, customer):
    return (
        has_permission(employee, "customers.update_owned")
        and customer.sales_id == employee.employee_id
    )


def can_update_contract(employee, contract):
    if has_permission(employee, "contracts.update_all"):
        return True

    return (
        has_permission(employee, "contracts.update_owned_customers")
        and contract.customer.sales_id == employee.employee_id
    )


def can_create_event(employee, contract):
    return (
        has_permission(
            employee,
            "events.create_for_signed_contract_owned_customers",
        )
        and contract.is_signed is True
        and contract.customer.sales_id == employee.employee_id
    )


def can_update_event(employee, event):
    if has_permission(employee, "events.assign_support"):
        return True

    return (
        has_permission(employee, "events.update_assigned")
        and event.support_id == employee.employee_id
    )


def can_filter_events_without_support(employee):
    return has_permission(employee, "events.filter_without_support")


def can_filter_my_events(employee) -> bool:
    return has_permission(employee, "events.filter_assigned_to_me")
