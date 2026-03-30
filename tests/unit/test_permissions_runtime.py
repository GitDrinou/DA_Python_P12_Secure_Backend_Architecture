from security import has_permission
from security.permissions import (
    ROLE_ADMIN,
    PERM_PERMISSIONS_CREATE,
    PERM_ROLE_PERMISSIONS_ASSIGN,
    PERM_CUSTOMERS_CREATE_OWNED,
    PERM_EVENTS_UPDATE_ASSIGNED,
)
from security.rbac import seed_rbac
from tests.factories import create_employee


def test_admin_employee_has_rbac_admin_permissions(db_session):
    seed_rbac(db_session)

    admin_employee = create_employee(
        db_session=db_session,
        role_name=ROLE_ADMIN,
        full_name="Admin Runtime",
        email="admin-runtime@test.com",
        password="Password123!",
    )

    assert has_permission(admin_employee, PERM_PERMISSIONS_CREATE) is True
    assert has_permission(admin_employee, PERM_ROLE_PERMISSIONS_ASSIGN) is True
    assert has_permission(admin_employee, PERM_CUSTOMERS_CREATE_OWNED) is True
    assert has_permission(admin_employee, PERM_EVENTS_UPDATE_ASSIGNED) is True
