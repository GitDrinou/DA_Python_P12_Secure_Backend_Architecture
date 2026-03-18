import pytest
from datetime import timezone, datetime, timedelta
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from database.models import Role, Employee, Customer, Contract, Event, \
    Permission


def test_create_full_crm_flow(db_session):
    """
        Check the crm flow
        role -> employee -> customer -> contract -> event
    """
    sales_role = Role(name="sales")
    support_role = Role(name="support")
    db_session.add_all([sales_role, support_role])
    db_session.commit()

    db_session.refresh(sales_role)
    db_session.refresh(support_role)

    sales_employee = Employee(
        full_name="Alice Sales",
        email="alice.sales@mail.com",
        password_hash="hashed_sales",
        is_active=True,
        role_id=sales_role.role_id,
    )

    support_employee = Employee(
        full_name="Bob Support",
        email="bob.support@mail.com",
        password_hash="hashed_support",
        is_active=True,
        role_id=support_role.role_id,
    )

    db_session.add_all([sales_employee, support_employee])
    db_session.commit()

    db_session.refresh(sales_employee)
    db_session.refresh(support_employee)

    customer = Customer(
        full_name="Paul Customer",
        email="paul.customer@megtronic.com",
        phone="0601020304",
        company_name="Megatronic Company",
        sales_id=sales_employee.employee_id,
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    contract = Contract(
        total_amount=Decimal("10000.00"),
        remaining_amount=Decimal("2500.00"),
        is_signed=True,
        customers_id=customer.customer_id,
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    event = Event(
        title="Team Building",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(hours=8),
        location="Paris",
        attendees=10,
        notes="Prévoir l'accueil avec petit-déjeuner",
        contract_id=contract.contract_id,
        support_id=support_employee.employee_id,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    assert customer.sales.employee_id == sales_employee.employee_id
    assert contract.customer.customer_id == customer.customer_id
    assert event.contract.contract_id == contract.contract_id
    assert event.support.employee_id == support_employee.employee_id
    assert event.contract.customer.company_name == "Megatronic Company"


def test_employee_email_must_be_unique(db_session, role_sales):
    employee_1 = Employee(
        full_name="Employee 1",
        email="employee@mail.com",
        password_hash="hashed_pass1",
        is_active=True,
        role_id=role_sales.role_id,
    )

    employee_2 = Employee(
        full_name="Employee 2",
        email="employee@mail.com",
        password_hash="hashed_pass2",
        is_active=True,
        role_id=role_sales.role_id,
    )

    db_session.add(employee_1)
    db_session.commit()

    db_session.add(employee_2)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_customer_email_must_be_unique(db_session, sales_employee):
    customer_1 = Customer(
        full_name="Customer 1",
        email="customer@mail.com",
        phone="0601020304",
        company_name="Company 1",
        sales_id=sales_employee.employee_id,
    )

    customer_2 = Customer(
        full_name="Customer 2",
        email="customer@mail.com",
        phone="0601020304",
        company_name="Company 2",
        sales_id=sales_employee.employee_id,
    )

    db_session.add(customer_1)
    db_session.commit()

    db_session.add(customer_2)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_permission_code_must_be_unique(db_session):
    permission_1 = Permission(
        code="management_customers",
        description="Can manage customers",
    )

    permission_2 = Permission(
        code="management_customers",
        description="Doublon",
    )

    db_session.add(permission_1)
    db_session.commit()

    db_session.add(permission_2)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_customer_must_reference_existing_sales(db_session):
    customer = Customer(
        full_name="Client Test",
        email="client-test@mail.com",
        phone="0601020304",
        company_name="Company Test",
        sales_id="non-existent-id",
    )

    db_session.add(customer)
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_contract_must_reference_existing_customer(db_session):
    contract = Contract(
        total_amount=Decimal("1500.00"),
        remaining_amount=Decimal("500.00"),
        is_signed=False,
        customers_id="non-existent-id",
    )

    db_session.add(contract)
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_event_must_reference_existing_contract(db_session, support_employee):
    event = Event(
        title="Team Building",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(hours=4),
        location="Paris",
        attendees=10,
        notes="Prévoir un goûter",
        contract_id="non-existent-id",
        support_id=support_employee.employee_id,
    )

    db_session.add(event)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_event_must_reference_existing_support_employee(db_session, contract):
    event = Event(
        title="Event Test",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(hours=2),
        location="Lyon",
        attendees=15,
        notes="Quelques notes de test",
        contract_id=contract.contract_id,
        support_id="non-existent-id",
    )

    db_session.add(event)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
