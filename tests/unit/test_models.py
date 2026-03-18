from datetime import datetime, timezone, timedelta
from decimal import Decimal

from database.models import Role, Employee, Customer, Contract, Event


def test_role_repr():
    role = Role(name="gestion")
    assert repr(role) == "<Role (name: gestion)>"


def test_employee_repr():
    employee = Employee(
        full_name="Jeanne Dupont",
        email="jeanne.dupont@mail.com",
        password_hash="hash_pass",
        is_active=True,
        role_id="fake_role_id"
    )
    assert "Jeanne Dupont" in repr(employee)
    assert "jeanne.dupont@mail.com" in repr(employee)


def test_customer_repr():
    customer = Customer(
        full_name="Client X",
        email="client.x@mail.com",
        phone="0600000000",
        company_name="Company XY",
        sales_id="fake_sales_id",
    )
    assert "Client X" in repr(customer)
    assert "client.x@mail.com" in repr(customer)


def test_contract_default_values(customer, db_session):
    contract = Contract(
        total_amount=Decimal("1000.00"),
        remaining_amount=Decimal("1000.00"),
        customers_id=customer.customer_id,
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    assert contract.is_signed is False
    assert contract.contract_id is not None
    assert contract.created_at is not None


def test_employee_role_relationship(db_session, role_sales):
    employee = Employee(
        full_name="Julien Commercial",
        email="julien.sales@mail.com",
        password_hash="hash_pass",
        is_active=True,
        role_id=role_sales.role_id,
    )

    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    assert employee.role.name == "commercial"


def test_customer_sales_relationship(db_session, sales_employee):
    customer = Customer(
        full_name="Josiane Durant",
        email="entreprise.a@mail.com",
        phone="0100000000",
        company_name="Entreprise A SAS",
        sales_id=sales_employee.employee_id,
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    assert customer.sales.full_name == "Alice Martin"


def test_event_creation(db_session, contract, support_employee):
    event = Event(
        title="Séminaire de printemps",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(hours=8),
        location="Bordeaux",
        attendees=80,
        notes="Prévoir le petit-déjeuner et le déjeuner en buffet",
        contract_id=contract.contract_id,
        support_id=support_employee.employee_id,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    assert event.event_id is not None
    assert event.title == "Séminaire de printemps"
    assert event.location == "Bordeaux"
    assert event.contract_id == contract.contract_id
    assert event.support_id == support_employee.employee_id


def test_event_relationships(db_session, contract, support_employee):
    event = Event(
        title="Salon du mariage",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=2),
        location="Paris",
        attendees=200,
        contract_id=contract.contract_id,
        support_id=support_employee.employee_id,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    assert event.contract.contract_id == contract.contract_id
    assert event.contract.customer.email == "client@example.com"
    assert event.support.full_name == "Bob Support"


def test_event_dates(db_session, contract, support_employee):
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=3)

    event = Event(
        title="Team Building",
        start_date=start,
        end_date=end,
        location="Lyon",
        attendees=10,
        contract_id=contract.contract_id,
        support_id=support_employee.employee_id,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    assert event.end_date > event.start_date
