from cli.commands import events
from datetime import datetime, timedelta, timezone
from tests.factories import (
    create_employee, create_customer, create_contract, create_event,
)
from tests.helpers.auth import (
    login_as_sales, login_as_manager, login_as_support
)


def test_events_list_requires_login(monkeypatch, db_session, tmp_path, capsys):
    from security import session_store

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    exit_code = events.main(
        db_session=db_session,
        args=["list"],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "No active session" in output


def test_events_create_as_sales(monkeypatch, db_session, tmp_path, capsys):

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

    exit_code = events.main(
        db_session=db_session,
        args=[
            "create",
            "--contract-id", contract.contract_id,
            "--title", "Customer Kickoff",
            "--start-date", start.isoformat(),
            "--end-date", end.isoformat(),
            "--location", "Paris",
            "--attendees", "20",
            "--notes", "Initial meeting",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Event created" in output


def test_events_create_as_manager_unauthorized(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):

    login_as_manager(monkeypatch, db_session, tmp_path)
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

    exit_code = events.main(
        db_session=db_session,
        args=[
            "create",
            "--contract-id", contract.contract_id,
            "--title", "Forbidden Event",
            "--start-date", start.isoformat(),
            "--end-date", end.isoformat(),
            "--location", "Paris",
            "--attendees", "20",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "events.create_for_signed_contract_owned_customers" in output


def test_events_update_as_support_on_assigned_event(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):

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

    exit_code = events.main(
        db_session=db_session,
        args=[
            "update",
            "--event-id", event.event_id,
            "--title", event.title,
            "--start-date", event.start_date.isoformat(),
            "--end-date", event.end_date.isoformat(),
            "--location", "Bordeaux",
            "--attendees", "75",
            "--notes", "Updated by support",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Event updated" in output


def test_events_update_as_support_on_unassigned_event_unauthorized(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):

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

    exit_code = events.main(
        db_session=db_session,
        args=[
            "update",
            "--event-id", event.event_id,
            "--title", event.title,
            "--start-date", event.start_date.isoformat(),
            "--end-date", event.end_date.isoformat(),
            "--location", "Lille",
            "--attendees", str(event.attendees),
            "--notes", event.notes or "",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "You are not allowed to update event" in output


def test_events_assign_support_as_manager(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):

    login_as_manager(monkeypatch, db_session, tmp_path)
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

    exit_code = events.main(
        db_session=db_session,
        args=[
            "assign-support",
            "--event-id", event.event_id,
            "--support-id", support.employee_id,
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Support assigned to event" in output


def test_events_assign_support_as_support_unauthorized(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):

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

    exit_code = events.main(
        db_session=db_session,
        args=[
            "assign-support",
            "--event-id", event.event_id,
            "--support-id", other_support.employee_id,
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "events.assign_support" in output


def test_events_list_without_support_as_manager(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):

    login_as_manager(monkeypatch, db_session, tmp_path)
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales",
        email="sales.list.nosupport@test.com",
        password="Password123!",
    )
    support = create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Support",
        email="support.list.nosupport@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.list.nosupport@test.com",
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
        support_employee=None,
        title="No Support Event",
    )
    create_event(
        db_session=db_session,
        contract=contract,
        support_employee=support,
        title="Assigned Event",
    )

    exit_code = events.main(
        db_session=db_session,
        args=["list", "--without-support"],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Assigned Event" not in output


def test_events_list_assigned_to_me_as_support(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):

    support = login_as_support(monkeypatch, db_session, tmp_path)
    other_support = create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Other Support",
        email="other.support.listme@test.com",
        password="Password123!",
    )
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales",
        email="sales.listme@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.listme@test.com",
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
        title="My Assigned Event",
    )
    create_event(
        db_session=db_session,
        contract=contract,
        support_employee=other_support,
        title="Other Support Event",
    )

    assert support is not None

    exit_code = events.main(
        db_session=db_session,
        args=["list", "--assigned-to-me"],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "My event" in output
    assert "Other Support Event" not in output


def test_events_delete_as_sales(monkeypatch, db_session, tmp_path, capsys):
    from tests.factories import create_event

    sales = login_as_sales(monkeypatch, db_session, tmp_path)
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.listme@test.com",
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
        title="My Assigned Event",
    )

    exit_code = events.main(
        db_session=db_session,
        args=[
            "delete",
            "--event-id", event.event_id,
            "--yes",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Event deleted" in output
