from security.rbac import seed_rbac
from services.employee_service import EmployeeService


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


def test_update_employee_email(db_session, sales_employee):
    service = EmployeeService(db_session)

    updated = service.update_employee(
        employee_id=sales_employee.employee_id,
        email="new.sales@example.com",
    )

    assert updated.email == "new.sales@example.com"


def test_delete_employee(db_session, sales_employee):
    service = EmployeeService(db_session)

    result = service.delete_employee(sales_employee.employee_id)

    assert result is True
