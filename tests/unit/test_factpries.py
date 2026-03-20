from security.permissions import ROLE_SALES
from security.rbac import seed_rbac
from tests.factories import (
    create_contract,
    create_customer,
    create_employee,
    create_event,
    unique_email,
)


def test_unique_email_generates_distinct_values():
    first = unique_email("tester")
    second = unique_email("tester")

    assert first != second
    assert first.endswith("@example.com")
    assert second.endswith("@example.com")


def test_create_employee_creates_persisted_employee(db_session):
    seed_rbac(db_session)

    employee = create_employee(
        db_session,
        role_name=ROLE_SALES,
        full_name="Alice Factory",
        email="alice.factory@example.com",
    )

    assert employee.employee_id is not None
    assert employee.role_id is not None
    assert employee.email == "alice.factory@example.com"
    assert employee.full_name == "Alice Factory"
    assert employee.password_hash != "Password123!"


def test_create_customer_contract_and_event_chain(db_session):
    seed_rbac(db_session)

    sales = create_employee(db_session, role_name=ROLE_SALES)
    customer = create_customer(db_session, sales)
    contract = create_contract(db_session, customer, is_signed=True)
    event = create_event(db_session, contract)

    assert customer.customer_id is not None
    assert customer.sales_id == sales.employee_id
    assert contract.contract_id is not None
    assert contract.customers_id == customer.customer_id
    assert event.event_id is not None
    assert event.contract_id == contract.contract_id
