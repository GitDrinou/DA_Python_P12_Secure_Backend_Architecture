from sqlalchemy.orm import joinedload
from database.models import Employee, Role
from security.jwt_handler import decode_token
from security.permissions import PERM_CUSTOMERS_UPDATE_OWNED, \
    PERM_CONTRACTS_UPDATE_ALL, \
    PERM_EVENTS_CREATE_FOR_SIGNED_CONTRACT_OWNED_CUSTOMERS, \
    PERM_EVENTS_ASSIGN_SUPPORT, PERM_EVENTS_UPDATE_ASSIGNED, \
    PERM_EVENTS_FILTER_WITHOUT_SUPPORT, PERM_EVENTS_FILTER_ASSIGNED_TO_ME


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
        has_permission(employee, PERM_CUSTOMERS_UPDATE_OWNED)
        and customer.sales_id == employee.employee_id
    )


def can_update_contract(employee, contract):
    if has_permission(employee, PERM_CONTRACTS_UPDATE_ALL):
        return True

    return (
        has_permission(employee, PERM_CUSTOMERS_UPDATE_OWNED)
        and contract.customer.sales_id == employee.employee_id
    )


def can_create_event(employee, contract):
    return (
        has_permission(
            employee,
            PERM_EVENTS_CREATE_FOR_SIGNED_CONTRACT_OWNED_CUSTOMERS,
        )
        and contract.is_signed is True
        and contract.customer.sales_id == employee.employee_id
    )


def can_update_event(employee, event):
    if has_permission(employee, PERM_EVENTS_ASSIGN_SUPPORT):
        return True

    return (
        has_permission(employee, PERM_EVENTS_UPDATE_ASSIGNED)
        and event.support_id == employee.employee_id
    )


def can_filter_events_without_support(employee):
    return has_permission(employee, PERM_EVENTS_FILTER_WITHOUT_SUPPORT)


def can_filter_my_events(employee) -> bool:
    return has_permission(employee, PERM_EVENTS_FILTER_ASSIGNED_TO_ME)
