from security.permissions import (
    PERM_CUSTOMERS_READ_ALL,
    PERM_CUSTOMERS_UPDATE_OWNED,
    PERM_EMPLOYEES_DELETE,
    ROLE_MANAGEMENT,
    ROLE_SALES,
    ROLE_SUPPORT
)
from security.rbac import seed_rbac
from security.authorization import (
    has_permission,
    can_update_customer,
    can_update_contract,
    can_create_event,
    can_update_event
)
from tests.factories import (
    create_employee,
    create_customer,
    create_contract,
    create_event
)


def test_has_permission_returns_true_for_role_permission(db_session):
    seed_rbac(db_session)

    commercial = create_employee(
        db_session,
        role_name=ROLE_SALES,
        full_name="Alice Sales",
        email="alice.sales@mail.com",
    )

    assert has_permission(commercial, PERM_CUSTOMERS_READ_ALL) is True
    assert has_permission(commercial, PERM_CUSTOMERS_UPDATE_OWNED) is True
    assert has_permission(commercial, PERM_EMPLOYEES_DELETE) is False


def test_sales_can_update_only_owned_customer(db_session):
    seed_rbac(db_session)

    alice = create_employee(
        db_session,
        ROLE_SALES,
        "Alice Sales",
        "alice@mail.com"
    )
    bob = create_employee(
        db_session,
        ROLE_SALES,
        "Bob Sales",
        "bob@mail.com"
    )

    alice_customer = create_customer(
        db_session,
        alice,
        email="alice.customer@mail.com"
    )
    bob_customer = create_customer(
        db_session,
        bob,
        email="bob.customer@mail.com"
    )

    assert can_update_customer(alice, alice_customer) is True
    assert can_update_customer(alice, bob_customer) is False


def test_management_can_update_any_contract(db_session):
    seed_rbac(db_session)

    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        "Manager",
        "manager@mail.com"
    )
    sales = create_employee(
        db_session,
        ROLE_SALES,
        "Alice Sales",
        "alice2@mail.com"
    )

    customer = create_customer(
        db_session,
        sales,
        email="contract.owner@mail.com"
    )
    contract = create_contract(db_session, customer)

    assert can_update_contract(manager, contract) is True


def test_sales_can_update_only_owned_customer_contract(db_session):
    seed_rbac(db_session)

    alice = create_employee(
        db_session,
        ROLE_SALES,
        "Alice Sales",
        "alice3@mail.com"
    )
    bob = create_employee(
        db_session,
        ROLE_SALES,
        "Bob Sales",
        "bob3@mail.com"
    )

    alice_customer = create_customer(
        db_session, alice, email="alice.contract@mail.com"
    )
    bob_customer = create_customer(
        db_session, bob, email="bob.contract@mail.com"
    )

    alice_contract = create_contract(db_session, alice_customer)
    bob_contract = create_contract(db_session, bob_customer)

    assert can_update_contract(alice, alice_contract) is True
    assert can_update_contract(alice, bob_contract) is False


def test_sales_can_create_event_only_for_signed_owned_contract(db_session):
    seed_rbac(db_session)

    alice = create_employee(
        db_session,
        ROLE_SALES,
        "Alice Sales",
        "alice4@mail.com"
    )
    bob = create_employee(
        db_session,
        ROLE_SALES,
        "Bob Sales",
        "bob4@mail.com"
    )

    alice_customer = create_customer(
        db_session, alice, email="alice.event@mail.com"
    )
    bob_customer = create_customer(
        db_session, bob, email="bob.event@mail.com"
    )

    signed_owned_contract = create_contract(
        db_session,
        alice_customer,
        is_signed=True
    )
    unsigned_owned_contract = create_contract(
        db_session,
        alice_customer,
        is_signed=False,
        total_amount="2000.00",
        remaining_amount="2000.00",
    )
    signed_other_contract = create_contract(
        db_session,
        bob_customer,
        is_signed=True
    )

    assert can_create_event(alice, signed_owned_contract) is True
    assert can_create_event(alice, unsigned_owned_contract) is False
    assert can_create_event(alice, signed_other_contract) is False


def test_support_can_update_only_assigned_event(db_session):
    seed_rbac(db_session)

    sales = create_employee(
        db_session,
        ROLE_SALES,
        "Sales",
        "sales@mail.com"
    )
    support_a = create_employee(
        db_session,
        ROLE_SUPPORT,
        "Support A",
        "support.a@mail.com"
    )
    support_b = create_employee(
        db_session,
        ROLE_SUPPORT,
        "Support B",
        "support.b@mail.com"
    )

    customer = create_customer(db_session, sales,
                               email="support.customer@mail.com")
    contract = create_contract(db_session, customer, is_signed=True)

    event_a = create_event(db_session, contract, support_employee=support_a)
    event_b = create_event(db_session, contract, support_employee=support_b)

    assert can_update_event(support_a, event_a) is True
    assert can_update_event(support_a, event_b) is False


def test_management_can_assign_support_on_any_event(db_session):
    seed_rbac(db_session)

    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        "Manager",
        "manager2@mail.com"
    )
    sales = create_employee(
        db_session,
        ROLE_SALES,
        "Sales",
        "sales2@mail.com"
    )
    support = create_employee(
        db_session,
        ROLE_SUPPORT,
        "Support",
        "support@mail.com"
    )

    customer = create_customer(db_session, sales,
                               email="manager.event@mail.com")
    contract = create_contract(db_session, customer, is_signed=True)
    event = create_event(db_session, contract, support_employee=support)

    assert can_update_event(manager, event) is True
