import pytest
from security.rbac import seed_rbac
from services.customer_service import CustomerService
from services.employee_service import EmployeeService
from tests.factories import create_employee, create_customer


def test_list_customers_returns_ordered_customers(db_session):
    seed_rbac(db_session)

    sales_employee = create_employee(
        db_session,
        "commercial",
        full_name="Sales User",
        email="sales@test.com",
        password="Password123!",
    )

    create_customer(
        db_session,
        sales_employee,
        full_name="Zombie Client",
        email="zombie@test.com",
    )
    create_customer(
        db_session,
        sales_employee,
        full_name="Angel Client",
        email="angel@test.com",
    )

    service = CustomerService(db_session)
    customers = service.list_customers()

    assert len(customers) == 2
    assert customers[0].full_name == "Angel Client"
    assert customers[1].full_name == "Zombie Client"


def test_get_customer_returns_customer(db_session):
    seed_rbac(db_session)

    sales_employee = create_employee(db_session, "commercial")
    customer = create_customer(
        db_session,
        sales_employee,
        full_name="Client A",
        email="client-a@test.com",
    )

    service = CustomerService(db_session)
    result = service.get_customer(customer.customer_id)

    assert result.customer_id == customer.customer_id
    assert result.email == "client-a@test.com"


def test_get_customer_raises_when_missing(db_session):
    seed_rbac(db_session)

    service = CustomerService(db_session)

    with pytest.raises(ValueError, match="Customer not found"):
        service.get_customer("999999")


def test_create_customer(db_session):
    seed_rbac(db_session)

    sales_employee = create_employee(
        db_session,
        "commercial",
        full_name="Alice Sales",
        email="alice-sales@test.com",
        password="Password123!",
    )

    service = CustomerService(db_session)
    customer = service.create_customer(
        current_employee=sales_employee,
        full_name="Jean Dupont",
        email="jean.dupont@example.com",
        phone="0102030405",
        company_name="Jean TestCompany",
    )

    assert customer.customer_id is not None
    assert customer.email == "jean.dupont@example.com"
    assert customer.company_name == "Jean TestCompany"
    assert customer.sales_id == sales_employee.employee_id


def test_create_customer_rejects_duplicate_email(db_session):
    seed_rbac(db_session)

    sales_employee = create_employee(db_session, "commercial")
    create_customer(
        db_session,
        sales_employee,
        full_name="Client 1",
        email="duplicate@test.com",
    )

    service = CustomerService(db_session)

    with pytest.raises(ValueError, match="Customer already exists"):
        service.create_customer(
            current_employee=sales_employee,
            full_name="Client 2",
            email="duplicate@test.com",
            phone="0102030405",
            company_name="Another Company",
        )


def test_create_customer_rejects_employee_without_permission(db_session):
    seed_rbac(db_session)

    support_employee = create_employee(
        db_session,
        "support",
        full_name="Support User",
        email="support-create@test.com",
        password="Password123!",
    )

    service = CustomerService(db_session)

    with pytest.raises(
            ValueError,
            match="You are not allowed to create customer"
    ):
        service.create_customer(
            current_employee=support_employee,
            full_name="Forbidden Customer",
            email="forbidden@test.com",
            phone="0102030405",
            company_name="Forbidden Company",
        )


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


def test_update_customer_rejects_non_owner(db_session):
    seed_rbac(db_session)

    owner = create_employee(
        db_session,
        "commercial",
        full_name="Owner",
        email="owner@test.com",
        password="Password123!",
    )
    other_sales = create_employee(
        db_session,
        "commercial",
        full_name="Other Sales",
        email="other-sales@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session,
        owner,
        full_name="Protected Customer",
        email="protected@test.com",
    )

    service = CustomerService(db_session)

    with pytest.raises(
            ValueError,
            match="You are not allowed to update customer"
    ):
        service.update_customer(
            current_employee=other_sales,
            customer_id=customer.customer_id,
            full_name="Illegal Update",
        )


def test_delete_customer(db_session, customer):
    seed_rbac(db_session)
    service = CustomerService(db_session)

    employee = (EmployeeService(db_session)
                .get_employee(employee_id=customer.sales_id))

    result = service.delete_customer(employee, customer.customer_id)

    assert result is True


def test_delete_customer_rejects_non_owner(db_session):
    seed_rbac(db_session)

    owner = create_employee(
        db_session,
        "commercial",
        full_name="Owner Delete",
        email="owner-delete@test.com",
        password="Password123!",
    )
    other_sales = create_employee(
        db_session,
        "commercial",
        full_name="Other Delete",
        email="other-delete@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session,
        owner,
        full_name="Protected Delete",
        email="protected-delete@test.com",
    )

    service = CustomerService(db_session)

    with pytest.raises(
            ValueError,
            match="You are not allowed to delete customer"
    ):
        service.delete_customer(
            current_employee=other_sales,
            customer_id=customer.customer_id,
        )
