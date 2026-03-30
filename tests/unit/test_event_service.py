import pytest
from datetime import datetime, timezone, timedelta
from security.permissions import ROLE_SALES, ROLE_SUPPORT, ROLE_MANAGEMENT
from security.rbac import seed_rbac
from services.event_service import EventService
from tests.factories import (
    create_employee,
    create_customer,
    create_contract,
    create_event,
)


def test_list_events(db_session):
    seed_rbac(db_session)

    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com",
    )
    support = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Support",
        email="support@test.com",
    )
    customer = create_customer(
        db_session,
        sales,
        full_name="Customer",
        email="customer@test.com",
    )
    contract = create_contract(
        db_session,
        customer,
        total_amount=1000.0,
        remaining_amount=0.0,
        is_signed=True,
    )
    create_event(
        db_session,
        contract,
        support_employee=support,
        title="Launch Event",
    )

    service = EventService(db_session)
    events = service.list_events()

    assert len(events) >= 1
    assert any(event.title == "Launch Event" for event in events)


def test_sales_can_create_event_for_signed_owned_contract(db_session):
    seed_rbac(db_session)
    service = EventService(db_session)

    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales Event",
        email="sales.event@test.com",
    )
    customer = create_customer(db_session, sales, email="cust.event@test.com")
    contract = create_contract(
        db_session,
        customer,
        is_signed=True,
        total_amount="1000.00",
        remaining_amount="0.00",
    )

    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = start + timedelta(hours=4)

    event = service.create_event(
        current_employee=sales,
        contract_id=contract.contract_id,
        title="Demo Event",
        start_date=start,
        end_date=end,
        location="Paris",
        attendees=25,
        notes="Important customer meeting",
    )

    assert event.event_id is not None
    assert event.title == "Demo Event"
    assert event.contract_id == contract.contract_id
    assert event.support_id is None


def test_sales_cannot_create_event_for_unsigned_contract(db_session):
    seed_rbac(db_session)
    service = EventService(db_session)

    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales Event",
        email="sales.event.unsigned@test.com",
    )
    customer = create_customer(
        db_session,
        sales,
        email="cust.unsigned@test.com"
    )
    contract = create_contract(
        db_session,
        customer,
        is_signed=False,
        total_amount="1000.00",
        remaining_amount="1000.00",
    )

    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = start + timedelta(hours=2)

    with pytest.raises(
            ValueError,
            match="You are not allowed to create event"
    ):
        service.create_event(
            current_employee=sales,
            contract_id=contract.contract_id,
            title="Unsigned Contract Event",
            start_date=start,
            end_date=end,
            location="Lyon",
            attendees=10,
        )


def test_sales_cannot_create_event_for_other_sales_contract(db_session):
    seed_rbac(db_session)
    service = EventService(db_session)

    alice = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Alice Sales",
        email="alice.event@test.com",
    )
    bob = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Bob Sales",
        email="bob.event@test.com",
    )

    customer = create_customer(
        db_session,
        bob,
        email="bob.customer.event@test.com"
    )
    contract = create_contract(
        db_session,
        customer,
        is_signed=True,
        total_amount="1000.00",
        remaining_amount="0.00",
    )

    start = datetime.now(timezone.utc) + timedelta(days=2)
    end = start + timedelta(hours=3)

    with pytest.raises(
            ValueError,
            match="You are not allowed to create event"
    ):
        service.create_event(
            current_employee=alice,
            contract_id=contract.contract_id,
            title="Forbidden Event",
            start_date=start,
            end_date=end,
            location="Marseille",
            attendees=15,
        )


def test_manager_can_assign_support_to_event(db_session):
    seed_rbac(db_session)
    service = EventService(db_session)

    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager Event",
        email="manager.event@test.com",
    )
    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales Event",
        email="sales.assign@test.com",
    )
    support = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Support Event",
        email="support.assign@test.com",
    )

    customer = create_customer(
        db_session,
        sales,
        email="cust.assign@test.com"
    )
    contract = create_contract(
        db_session,
        customer,
        is_signed=True,
        remaining_amount="0.00"
    )
    event = create_event(db_session, contract)

    updated = service.assign_support(
        event_id=event.event_id,
        current_employee=manager,
        support_id=support.employee_id,
    )

    assert updated.support_id == support.employee_id


def test_support_cannot_assign_support_to_event(db_session):
    seed_rbac(db_session)
    service = EventService(db_session)

    support_actor = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Support Actor",
        email="support.actor@test.com",
    )
    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales Event",
        email="sales.support.assign@test.com",
    )
    other_support = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Other Support",
        email="support.other@test.com",
    )

    customer = create_customer(
        db_session,
        sales,
        email="cust.support.assign@test.com"
    )
    contract = create_contract(
        db_session,
        customer,
        is_signed=True,
        remaining_amount="0.00"
    )
    event = create_event(db_session, contract)

    with pytest.raises(
        ValueError,
        match="You are not allowed to assign support",
    ):
        service.assign_support(
            event_id=event.event_id,
            current_employee=support_actor,
            support_id=other_support.employee_id,
        )


def test_support_can_update_assigned_event(db_session):
    seed_rbac(db_session)
    service = EventService(db_session)

    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales Event",
        email="sales.update.assigned@test.com",
    )
    support = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Assigned Support",
        email="support.update.assigned@test.com",
    )

    customer = create_customer(
        db_session,
        sales,
        email="cust.update.assigned@test.com"
    )
    contract = create_contract(
        db_session,
        customer,
        is_signed=True,
        remaining_amount="0.00"
    )
    event = create_event(db_session, contract, support_employee=support)

    updated = service.update_event(
        event_id=event.event_id,
        current_employee=support,
        location="Bordeaux",
        attendees=80,
        notes="Updated by support",
    )

    assert updated.location == "Bordeaux"
    assert updated.attendees == 80
    assert updated.notes == "Updated by support"


def test_support_cannot_update_unassigned_event(db_session):
    seed_rbac(db_session)
    service = EventService(db_session)

    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales Event",
        email="sales.unassigned@test.com",
    )
    support = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Unassigned Support",
        email="support.unassigned@test.com",
    )

    customer = create_customer(
        db_session,
        sales,
        email="cust.unassigned@test.com"
    )
    contract = create_contract(
        db_session,
        customer,
        is_signed=True,
        remaining_amount="0.00"
    )
    event = create_event(db_session, contract)

    with pytest.raises(
            ValueError,
            match="You are not allowed to update event"
    ):
        service.update_event(
            event_id=event.event_id,
            current_employee=support,
            location="Nice",
        )


def test_manager_can_update_any_event(db_session):
    seed_rbac(db_session)
    service = EventService(db_session)

    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager Event",
        email="manager.update.event@test.com",
    )
    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales Event",
        email="sales.update.event@test.com",
    )
    customer = create_customer(
        db_session,
        sales,
        email="cust.manager.update@test.com"
    )
    contract = create_contract(
        db_session,
        customer,
        is_signed=True,
        remaining_amount="0.00"
    )
    event = create_event(db_session, contract)

    updated = service.update_event(
        event_id=event.event_id,
        current_employee=manager,
        title="Updated Title",
        attendees=120,
    )

    assert updated.title == "Updated Title"
    assert updated.attendees == 120


def test_list_events_without_support_allows_management(db_session):
    seed_rbac(db_session)

    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager",
        email="manager@test.com"
    )
    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com"
    )
    support = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Support",
        email="support@test.com"
    )
    customer = create_customer(
        db_session,
        sales,
        full_name="Customer",
        email="customer@test.com"
    )
    contract = create_contract(
        db_session,
        customer,
        total_amount=1400.0,
        remaining_amount=0.0,
        is_signed=True
    )
    unassigned = create_event(
        db_session,
        contract,
        support_employee=None,
        title="Unassigned Event"
    )
    create_event(
        db_session,
        contract,
        support_employee=support,
        title="Assigned Event"
    )

    service = EventService(db_session)
    events = service.list_events_without_support(current_employee=manager)
    event_ids = {event.event_id for event in events}

    assert unassigned.event_id in event_ids


def test_list_my_events_allows_support(db_session):
    seed_rbac(db_session)

    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com"
    )
    support = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Support",
        email="support@test.com"
    )
    other_support = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Other Support",
        email="other-support@test.com")
    customer = create_customer(
        db_session,
        sales,
        full_name="Customer",
        email="customer@test.com"
    )
    contract = create_contract(
        db_session,
        customer,
        total_amount=1700.0,
        remaining_amount=0.0,
        is_signed=True
    )
    my_event = create_event(
        db_session,
        contract,
        support_employee=support,
        title="My Event"
    )
    create_event(
        db_session,
        contract,
        support_employee=other_support,
        title="Other Support Event"
    )

    service = EventService(db_session)
    events = service.list_my_events(current_employee=support)
    event_ids = {event.event_id for event in events}

    assert my_event.event_id in event_ids
