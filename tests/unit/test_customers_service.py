from security.rbac import seed_rbac
from services.customer_service import CustomerService
from services.employee_service import EmployeeService


def test_create_customer(db_session):
    seed_rbac(db_session)
    service_employee = EmployeeService(db_session)
    service_customer = CustomerService(db_session)

    employee = service_employee.create_employee(
        full_name="Jean Dupont",
        email="jean.dupont@example.com",
        password="Password123!",
        role_name="commercial",
    )

    customer = service_customer.create_customer(
        full_name="Jean Dupont",
        email="jean.dupont@example.com",
        phone="123-456-7890",
        company_name="Jean TestCompany",
        current_employee=employee,
    )

    assert customer.customer_id is not None
    assert customer.email == "jean.dupont@example.com"
    assert customer.company_name == "Jean TestCompany"
    assert customer.sales_id == employee.employee_id


def test_update_customer_email(db_session, customer):
    seed_rbac(db_session)
    service = CustomerService(db_session)

    employee = (EmployeeService(db_session)
                .get_employee(employee_id=customer.sales_id))

    updated = service.update_customer(
        current_employee=employee,
        customer_id=customer.customer_id,
        email="new.sales@example.com",
    )

    assert updated.email == "new.sales@example.com"


def test_delete_customer(db_session, customer):
    seed_rbac(db_session)
    service = CustomerService(db_session)

    employee = (EmployeeService(db_session)
                .get_employee(employee_id=customer.sales_id))

    result = service.delete_customer(employee, customer.customer_id)

    assert result is True
