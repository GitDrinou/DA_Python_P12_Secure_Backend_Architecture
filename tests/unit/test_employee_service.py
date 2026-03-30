import pytest

from security.permissions import ROLE_MANAGEMENT, ROLE_SALES, ROLE_SUPPORT
from security.rbac import seed_rbac
from services.employee_service import EmployeeService
from tests.factories import create_employee


def test_list_employees_returns_all_employees(db_session):
    seed_rbac(db_session)

    create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager A",
        email="manager-a@test.com",
    )
    create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales B",
        email="sales-b@test.com",
    )
    create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Support C",
        email="support-c@test.com",
    )

    service = EmployeeService(db_session)
    employees = service.list_employees()

    assert len(employees) >= 3
    emails = {employee.email for employee in employees}
    assert "manager-a@test.com" in emails
    assert "sales-b@test.com" in emails
    assert "support-c@test.com" in emails


def test_get_employee(db_session):
    seed_rbac(db_session)

    employee = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com",
    )

    service = EmployeeService(db_session)
    result = service.get_employee(employee.employee_id)

    assert result.employee_id == employee.employee_id
    assert result.email == "sales@test.com"


def test_get_employee_raises_when_missing(db_session):
    seed_rbac(db_session)
    service = EmployeeService(db_session)

    with pytest.raises(ValueError, match="Employee not found"):
        service.get_employee("999999")


def test_create_employee_allows_management(db_session):
    seed_rbac(db_session)

    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager Creator",
        email='manager@test.com',
    )

    service = EmployeeService(db_session)
    employee = service.create_employee(
        current_employee=manager,
        full_name="New Support",
        email="support@test.com",
        password="Password123!",
        role_name=ROLE_SUPPORT,
    )

    assert employee.employee_id is not None
    assert employee.email == "support@test.com"
    assert employee.role.name == ROLE_SUPPORT


def test_create_employee_rejects_non_management(db_session):
    seed_rbac(db_session)
    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com",
    )
    service = EmployeeService(db_session)

    with pytest.raises(
            ValueError,
            match="You are not allowed to create employee"
    ):
        service.create_employee(
            current_employee=sales,
            full_name="Employee",
            email="employee@test.com",
            password="Password123!",
            role_name=ROLE_SUPPORT,
        )


def test_update_employee_email_allows_management(db_session, sales_employee):
    seed_rbac(db_session)
    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager",
        email="manager@test.com",
    )
    employee = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Support",
        email="support@test.com",
    )

    service = EmployeeService(db_session)
    updated = service.update_employee(
        current_employee=manager,
        employee_id=employee.employee_id,
        full_name="New Support",
        is_active=False,
    )

    assert updated.full_name == "New Support"
    assert updated.is_active is False


def test_update_employee_rejects_non_management(db_session):
    seed_rbac(db_session)

    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com"
    )
    support = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Support",
        email="support@test.com"
    )

    service = EmployeeService(db_session)

    with pytest.raises(
            ValueError,
            match="You are not allowed to update employee"
    ):
        service.update_employee(
            current_employee=sales,
            employee_id=support.employee_id,
            full_name="Illegal Update",
        )


def test_update_employee_rejects_duplicate_email(db_session):
    seed_rbac(db_session)
    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager",
        email="manager@test.com",
    )
    employee_1 = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Employee One",
        email="employee-one@test.com",
    )
    employee_2 = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Employee Two",
        email="employee-two@test.com",
    )

    service = EmployeeService(db_session)

    with pytest.raises(ValueError, match="Employee already exists"):
        service.update_employee(
            current_employee=manager,
            employee_id=employee_2.employee_id,
            email=employee_1.email,
        )


def test_delete_employee(db_session, sales_employee):
    seed_rbac(db_session)
    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager",
        email="manager@test.com",
    )
    employee = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Support",
        email="support@test.com",
    )
    service = EmployeeService(db_session)
    result = service.delete_employee(
        current_employee=manager,
        employee_id=employee.employee_id,
    )

    assert result is True
