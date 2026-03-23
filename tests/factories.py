from datetime import datetime, timezone, timedelta
from decimal import Decimal
from itertools import count

from database.models import Role, Employee, Customer, Contract, Event
from security.passwords import hash_password

_email_counter = count(1)
_company_counter = count(1)
_phone_counter = count(1)


def unique_email(prefix="user"):
    index = next(_email_counter)
    return f"{prefix}{index}@example.com"


def unique_company(prefix="company"):
    index = next(_company_counter)
    return f"{prefix}{index}@example.com"


def unique_phone(prefix="phone"):
    index = next(_phone_counter)
    return f"{prefix}{index}@example.com"


def get_role(db_session, role_name):
    return db_session.query(Role).filter(Role.name == role_name).first()


def create_employee(
    db_session,
    role_name,
    full_name="Test Employee",
    email=None,
    password="Password123!",
    is_active=True,
):
    role = get_role(db_session, role_name)
    if role is None:
        raise ValueError(f"Unknown role: {role_name}")

    employee = Employee(
        full_name=full_name or f"{role_name.title()} Employee",
        email=email or unique_email(role_name),
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
    full_name="Client Test",
    email=None,
    phone=None,
    company_name=None,
):
    customer = Customer(
        full_name=full_name,
        email=email or unique_email("customer"),
        phone=phone or unique_phone(),
        company_name=company_name or unique_company("ACME"),
        sales_id=sales_employee.employee_id,
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


def create_contract(
    db_session,
    customer,
    is_signed=False,
    total="1000.00",
    remaining="1000.00",
):
    contract = Contract(
        total_amount=Decimal(total),
        remaining_amount=Decimal(remaining),
        is_signed=is_signed,
        customers_id=customer.customer_id,
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)
    return contract


def create_event(
    db_session,
    contract,
    support_employee=None,
    title="Salon",
    location="Paris",
    attendees=50,
    notes="Test event",
    start_date=None,
    end_date=None,
):
    start = start_date or datetime.now(timezone.utc)
    end = end_date or (start + timedelta(hours=4))

    event = Event(
        title=title,
        start_date=start,
        end_date=end,
        location=location,
        attendees=attendees,
        notes=notes,
        contract_id=contract.contract_id,
        support_id=support_employee.employee_id if support_employee else None,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event
