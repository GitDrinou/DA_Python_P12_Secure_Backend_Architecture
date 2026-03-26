import pytest
from security.rbac import seed_rbac
from services.employee_service import EmployeeService
from tests.factories import create_employee


def test_list_employees_returns_all_employees(db_session):
    seed_rbac(db_session)

    create_employee(
        db_session,
        "gestion",
        full_name="Manager A",
        email="manager-a@test.com",
    )
    create_employee(
        db_session,
        "commercial",
        full_name="Sales B",
        email="sales-b@test.com",
    )
    create_employee(
        db_session,
        "support",
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
        "commercial",
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


def test_create_employee(db_session):
    seed_rbac(db_session)
    service = EmployeeService(db_session)

    employee = service.create_employee(
        full_name="Jean Dupont",
        email="jean.dupont@example.com",
        password="Password123!",
        role_name="commercial",
    )

    assert employee.employee_id is not None
    assert employee.email == "jean.dupont@example.com"
    assert employee.role.name == "commercial"


def test_create_employee_rejects_unknown_role(db_session):
    seed_rbac(db_session)
    service = EmployeeService(db_session)

    with pytest.raises(ValueError, match="Role not found"):
        service.create_employee(
            full_name="Employee",
            email="employee@test.com",
            password="Password123!",
            role_name="unknown-role",
        )


def test_update_employee_email(db_session, sales_employee):
    service = EmployeeService(db_session)

    updated = service.update_employee(
        employee_id=sales_employee.employee_id,
        email="new.sales@example.com",
    )

    assert updated.email == "new.sales@example.com"


def test_update_employee_rejects_duplicate_email(db_session):
    seed_rbac(db_session)

    employee_1 = create_employee(
        db_session,
        "support",
        full_name="Employee One",
        email="employee-one@test.com",
    )
    employee_2 = create_employee(
        db_session,
        "commercial",
        full_name="Employee Two",
        email="employee-two@test.com",
    )

    service = EmployeeService(db_session)

    with pytest.raises(ValueError, match="Employee already exists"):
        service.update_employee(
            employee_id=employee_2.employee_id,
            email=employee_1.email,
        )


def test_delete_employee(db_session, sales_employee):
    service = EmployeeService(db_session)

    result = service.delete_employee(sales_employee.employee_id)

    assert result is True
