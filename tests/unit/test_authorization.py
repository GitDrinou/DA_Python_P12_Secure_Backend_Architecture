from decimal import Decimal
from datetime import datetime, timezone, timedelta

from database.models import Role, Employee, Customer, Contract, Event
from security.rbac import seed_rbac
from security.authorization import (
    has_permission,
    can_update_customer,
    can_update_contract,
    can_create_event,
    can_update_event
)


def _get_role(db_session, role_name):
    return db_session.query(Role).filter(Role.name == role_name).first()


def _create_employee(db_session, role_name, full_name, email):
    role = _get_role(db_session, role_name)
    employee = Employee(
        full_name=full_name,
        email=email,
        password_hash="hashed_password",
        is_active=True,
        role_id=role.role_id,
    )

    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    return employee


def _create_customer(db_session, sales_employee, email="customer@mail.com"):
    customer = Customer(
        full_name="Client Test",
        email=email,
        phone="0601020304",
        company_name="ACME",
        sales_id=sales_employee.employee_id,
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    return customer


def _create_contract(
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


def _create_event(db_session, contract, support_employee=None):
    event = Event(
        title="Salon",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(hours=4),
        location="Paris",
        attendees=50,
        notes="Test event",
        contract_id=contract.contract_id,
        support_id=support_employee.employee_id if support_employee else None,
    )

    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    return event


def test_has_permission_returns_true_for_role_permission(db_session):
    seed_rbac(db_session)

    commercial = _create_employee(
        db_session,
        role_name="commercial",
        full_name="Alice Sales",
        email="alice.sales@mail.com",
    )

    assert has_permission(commercial, "customers.read_all") is True
    assert has_permission(commercial, "customers.update_owned") is True
    assert has_permission(commercial, "employees.delete") is False


def test_sales_can_update_only_owned_customer(db_session):
    seed_rbac(db_session)

    alice = _create_employee(
        db_session,
        "commercial",
        "Alice Sales",
        "alice@mail.com"
    )
    bob = _create_employee(
        db_session,
        "commercial",
        "Bob Sales",
        "bob@mail.com"
    )

    alice_customer = _create_customer(
        db_session,
        alice,
        email="alice.customer@mail.com"
    )
    bob_customer = _create_customer(
        db_session,
        bob,
        email="bob.customer@mail.com"
    )

    assert can_update_customer(alice, alice_customer) is True
    assert can_update_customer(alice, bob_customer) is False


def test_management_can_update_any_contract(db_session):
    seed_rbac(db_session)

    manager = _create_employee(
        db_session,
        "gestion",
        "Manager",
        "manager@mail.com"
    )
    sales = _create_employee(
        db_session,
        "commercial",
        "Alice Sales",
        "alice2@mail.com"
    )

    customer = _create_customer(
        db_session,
        sales,
        email="contract.owner@mail.com"
    )
    contract = _create_contract(db_session, customer)

    assert can_update_contract(manager, contract) is True


def test_sales_can_update_only_owned_customer_contract(db_session):
    seed_rbac(db_session)

    alice = _create_employee(
        db_session,
        "commercial",
        "Alice Sales",
        "alice3@mail.com"
    )
    bob = _create_employee(
        db_session,
        "commercial",
        "Bob Sales",
        "bob3@mail.com"
    )

    alice_customer = _create_customer(
        db_session, alice, email="alice.contract@mail.com"
    )
    bob_customer = _create_customer(
        db_session, bob, email="bob.contract@mail.com"
    )

    alice_contract = _create_contract(db_session, alice_customer)
    bob_contract = _create_contract(db_session, bob_customer)

    assert can_update_contract(alice, alice_contract) is True
    assert can_update_contract(alice, bob_contract) is False


def test_sales_can_create_event_only_for_signed_owned_contract(db_session):
    seed_rbac(db_session)

    alice = _create_employee(
        db_session,
        "commercial",
        "Alice Sales",
        "alice4@mail.com"
    )
    bob = _create_employee(
        db_session,
        "commercial",
        "Bob Sales",
        "bob4@mail.com"
    )

    alice_customer = _create_customer(
        db_session, alice, email="alice.event@mail.com"
    )
    bob_customer = _create_customer(
        db_session, bob, email="bob.event@mail.com"
    )

    signed_owned_contract = _create_contract(
        db_session,
        alice_customer,
        is_signed=True
    )
    unsigned_owned_contract = _create_contract(
        db_session,
        alice_customer,
        is_signed=False,
        total="2000.00",
        remaining="2000.00",
    )
    signed_other_contract = _create_contract(
        db_session,
        bob_customer,
        is_signed=True
    )

    assert can_create_event(alice, signed_owned_contract) is True
    assert can_create_event(alice, unsigned_owned_contract) is False
    assert can_create_event(alice, signed_other_contract) is False


def test_support_can_update_only_assigned_event(db_session):
    seed_rbac(db_session)

    sales = _create_employee(
        db_session,
        "commercial",
        "Sales",
        "sales@mail.com"
    )
    support_a = _create_employee(
        db_session,
        "support",
        "Support A",
        "support.a@mail.com"
    )
    support_b = _create_employee(
        db_session,
        "support",
        "Support B",
        "support.b@mail.com"
    )

    customer = _create_customer(db_session, sales,
                                email="support.customer@mail.com")
    contract = _create_contract(db_session, customer, is_signed=True)

    event_a = _create_event(db_session, contract, support_employee=support_a)
    event_b = _create_event(db_session, contract, support_employee=support_b)

    assert can_update_event(support_a, event_a) is True
    assert can_update_event(support_a, event_b) is False


def test_management_can_assign_support_on_any_event(db_session):
    seed_rbac(db_session)

    manager = _create_employee(
        db_session,
        "gestion",
        "Manager",
        "manager2@mail.com"
    )
    sales = _create_employee(
        db_session,
        "commercial",
        "Sales",
        "sales2@mail.com"
    )
    support = _create_employee(
        db_session,
        "support",
        "Support",
        "support@mail.com"
    )

    customer = _create_customer(db_session, sales,
                                email="manager.event@mail.com")
    contract = _create_contract(db_session, customer, is_signed=True)
    event = _create_event(db_session, contract, support_employee=support)

    assert can_update_event(manager, event) is True
