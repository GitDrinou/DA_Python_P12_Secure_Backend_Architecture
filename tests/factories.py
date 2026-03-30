from datetime import datetime, timezone, timedelta
from decimal import Decimal
from database.models import Role, Employee, Customer, Contract, Event
from security.passwords import hash_password
from sqlalchemy import select

_employee_counter = 0
_customer_counter = 0
_event_counter = 0


def create_employee(
    db_session,
    role_name,
    full_name="Test Employee",
    email=None,
    password="Password123!",
    is_active=True,
):
    global _employee_counter
    _employee_counter += 1

    role = db_session.execute(
        select(Role).where(Role.name == role_name)
    ).scalar_one()

    employee = Employee(
        full_name=full_name or f"Employee {_employee_counter}",
        email=email or f"employee{_employee_counter}@test.com",
        password_hash=hash_password(password),
        is_active=is_active,
        role_id=role.role_id,
    )

    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    return employee


def create_customer(
    db_session,
    sales_employee,
    full_name=None,
    email=None,
    phone="0102030405",
    company_name="Test Company",
):
    global _customer_counter
    _customer_counter += 1

    customer = Customer(
        full_name=full_name or f"Customer {_customer_counter}",
        email=email or f"customer{_customer_counter}@test.com",
        phone=phone,
        company_name=company_name,
        sales_id=sales_employee.employee_id,
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    return customer


def create_contract(
    db_session,
    customer,
    total_amount=1000.0,
    remaining_amount=1000.0,
    is_signed=False,
):
    contract = Contract(
        customers_id=customer.customer_id,
        total_amount=Decimal(str(total_amount)),
        remaining_amount=Decimal(str(remaining_amount)),
        is_signed=is_signed,
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    return contract


def create_event(
    db_session,
    contract,
    support_employee=None,
    title=None,
    start_date=None,
    end_date=None,
    location="Paris",
    attendees=10,
    notes="Test event",
):
    global _event_counter
    _event_counter += 1

    event = Event(
        contract_id=contract.contract_id,
        support_id=support_employee.employee_id if support_employee else None,
        title=title or f"Event {_event_counter}",
        start_date=(
                start_date or datetime.now(timezone.utc) + timedelta(days=7)),
        end_date=(
                end_date
                or datetime.now(timezone.utc) + timedelta(days=7, hours=4)),
        location=location,
        attendees=attendees,
        notes=notes,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    return event
