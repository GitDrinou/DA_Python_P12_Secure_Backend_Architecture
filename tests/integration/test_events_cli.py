import sys
from datetime import datetime, timezone, timedelta
from tests.factories import (
    create_employee,
    create_customer,
    create_contract,
    create_event,
)
from tests.helpers.auth import (
    login_as_sales,
    login_as_manager,
    login_as_support
)


def test_events_list_requires_login(monkeypatch, capsys, tmp_path):
    from security import session_store
    import events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )
    monkeypatch.setattr(sys, "argv", ["events.py", "list"])

    exit_code = events.main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert (
        "[FORBIDDEN] No active session. "
        "Please login with: >> epic_events.py login <<"
    ) in output


def test_events_create_as_sales(
        monkeypatch,
        db_session,
        tmp_path,
        capsys):
    import events

    sales = login_as_sales(monkeypatch, db_session, tmp_path)
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.events.create@test.com",
    )
    contract = create_contract(
        db_session=db_session,
        customer=customer,
        is_signed=True,
        total_amount="1200.00",
        remaining_amount="0.00",
    )

    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = start + timedelta(hours=3)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "events.py",
            "create",
            "--contract-id",
            contract.contract_id,
            "--title",
            "Customer Kickoff",
            "--start-date",
            start.isoformat(),
            "--end-date",
            end.isoformat(),
            "--location",
            "Paris",
            "--attendees",
            "20",
            "--notes",
            "Initial meeting",
        ],
    )

    exit_code = events.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 0, output
    assert "[SUCCESS] Event created" in output


def test_events_create_as_manager_unauthorized(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import events

    manager = login_as_manager(monkeypatch, db_session, tmp_path)
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales",
        email="sales@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer@test.com",
    )
    contract = create_contract(
        db_session=db_session,
        customer=customer,
        is_signed=True,
        total_amount="1200.00",
        remaining_amount="0.00",
    )

    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = start + timedelta(hours=3)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "events.py",
            "create",
            "--contract-id",
            contract.contract_id,
            "--title",
            "Forbidden Event",
            "--start-date",
            start.isoformat(),
            "--end-date",
            end.isoformat(),
            "--location",
            "Paris",
            "--attendees",
            "20",
        ],
    )

    exit_code = events.main(db_session=db_session)
    output = capsys.readouterr().out

    assert manager is not None
    assert exit_code == 1
    assert (
        "[UNEXPECTED] You don't have permission: "
        "events.create_for_signed_contract_owned_customers"
    ) in output


def test_events_update_as_support_on_assigned_event(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import events

    support = login_as_support(monkeypatch, db_session, tmp_path)
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales",
        email="sales@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer@test.com",
    )
    contract = create_contract(
        db_session=db_session,
        customer=customer,
        is_signed=True,
        total_amount="1200.00",
        remaining_amount="0.00",
    )
    event = create_event(
        db_session=db_session,
        contract=contract,
        support_employee=support,
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "events.py",
            "update",
            "--event-id",
            event.event_id,
            "--location",
            "Bordeaux",
            "--attendees",
            "75",
        ],
    )

    exit_code = events.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 0, output
    assert "[SUCCESS] Event updated" in output


def test_events_update_as_support_on_unassigned_event_unauthorized(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import events

    login_as_support(monkeypatch, db_session, tmp_path)
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales",
        email="sales@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer@test.com",
    )
    contract = create_contract(
        db_session=db_session,
        customer=customer,
        is_signed=True,
        total_amount="1200.00",
        remaining_amount="0.00",
    )
    event = create_event(
        db_session=db_session,
        contract=contract,
        support_employee=None,
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "events.py",
            "update",
            "--event-id",
            event.event_id,
            "--location",
            "Lille",
        ],
    )

    exit_code = events.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 1, output
    assert "[ERROR] You are not allowed to update event" in output


def test_events_assign_support_as_manager(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import events

    manager = login_as_manager(monkeypatch, db_session, tmp_path)
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales",
        email="sales@test.com",
        password="Password123!",
    )
    support = create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Support",
        email="support@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer@test.com",
    )
    contract = create_contract(
        db_session=db_session,
        customer=customer,
        is_signed=True,
        total_amount="1200.00",
        remaining_amount="0.00",
    )
    event = create_event(db_session=db_session, contract=contract)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "events.py",
            "assign-support",
            "--event-id",
            event.event_id,
            "--support-id",
            support.employee_id,
        ],
    )

    exit_code = events.main(db_session=db_session)
    output = capsys.readouterr().out

    assert manager is not None
    assert exit_code == 0, output
    assert "[SUCCESS] Support assigned to event" in output


def test_events_assign_support_as_support_unauthorized(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import events

    login_as_support(monkeypatch, db_session, tmp_path)
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales",
        email="sales@test.com",
        password="Password123!",
    )
    other_support = create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Other Support",
        email="other.support@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer@test.com",
    )
    contract = create_contract(
        db_session=db_session,
        customer=customer,
        is_signed=True,
        total_amount="1200.00",
        remaining_amount="0.00",
    )
    event = create_event(db_session=db_session, contract=contract)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "events.py",
            "assign-support",
            "--event-id",
            event.event_id,
            "--support-id",
            other_support.employee_id,
        ],
    )

    exit_code = events.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert ("[UNEXPECTED] You don't have permission: "
            "events.assign_support") in output


def test_events_list_without_support_as_manager(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import events

    manager = login_as_manager(monkeypatch, db_session, tmp_path)
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales",
        email="sales@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.filter.without@test.com",
    )
    contract = create_contract(
        db_session=db_session,
        customer=customer,
        is_signed=True,
        total_amount="1200.00",
        remaining_amount="0.00",
    )
    create_event(
        db_session=db_session,
        contract=contract,
        support_employee=None
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "events.py",
            "list",
            "--without-support",
        ],
    )

    exit_code = events.main(db_session=db_session)
    output = capsys.readouterr().out

    assert manager is not None
    assert exit_code == 0, output
    assert "event_id" in output


def test_events_list_assigned_to_me_as_support(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import events

    support = login_as_support(monkeypatch, db_session, tmp_path)
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales",
        email="sales@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer@test.com",
    )
    contract = create_contract(
        db_session=db_session,
        customer=customer,
        is_signed=True,
        total_amount="1200.00",
        remaining_amount="0.00",
    )
    create_event(
        db_session=db_session,
        contract=contract,
        support_employee=support,
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "events.py",
            "list",
            "--assigned-to-me",
        ],
    )

    exit_code = events.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 0, output
    assert "event_id" in output


def test_events_list_without_support_as_support_unauthorized(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import events

    login_as_support(monkeypatch, db_session, tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "events.py",
            "list",
            "--without-support",
        ],
    )

    exit_code = events.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert (
        "[UNEXPECTED] You don't have permission: "
        "events.filter_without_support"
    ) in output
