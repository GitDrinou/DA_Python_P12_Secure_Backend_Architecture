from tests.factories import (
    create_contract,
    create_customer,
    create_employee,
    create_event,
)
from tests.helpers.auth import (
    login_as_manager,
    login_as_sales,
    login_as_support
)


def test_root_cli_employees_list(monkeypatch, db_session, tmp_path, capsys):
    import epic_events

    login_as_manager(monkeypatch, db_session, tmp_path)

    exit_code = epic_events.main(
        db_session=db_session,
        args=["employees", "list"],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Employees" in output


def test_root_cli_contracts_create(monkeypatch, db_session, tmp_path, capsys):
    import epic_events

    manager = login_as_manager(monkeypatch, db_session, tmp_path)
    customer = create_customer(
        db_session=db_session,
        sales_employee=manager,
        email="customer.root.contracts@test.com",
    )

    exit_code = epic_events.main(
        db_session=db_session,
        args=[
            "contracts",
            "create",
            "--customer-id",
            customer.customer_id,
            "--total-amount",
            "1500",
            "--remaining-amount",
            "500",
            "--is-signed",
            "false",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Contract created" in output


def test_root_cli_events_update(monkeypatch, db_session, tmp_path, capsys):
    import epic_events

    support = login_as_support(monkeypatch, db_session, tmp_path)
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales Root",
        email="sales.root.events@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.root.events@test.com",
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

    exit_code = epic_events.main(
        db_session=db_session,
        args=[
            "events",
            "update",
            "--event-id",
            event.event_id,
            "--title",
            event.title,
            "--start-date",
            event.start_date.isoformat(),
            "--end-date",
            event.end_date.isoformat(),
            "--location",
            "Marseille",
            "--attendees",
            str(event.attendees),
            "--notes",
            "Updated from root CLI",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Event updated" in output


def test_root_cli_customers_create(monkeypatch, db_session, tmp_path, capsys):
    import epic_events

    login_as_sales(monkeypatch, db_session, tmp_path)

    exit_code = epic_events.main(
        db_session=db_session,
        args=[
            "customers",
            "create",
            "--full-name",
            "Customer Root",
            "--email",
            "customer.root@test.com",
            "--phone",
            "0102030405",
            "--company-name",
            "Root Company",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Customer created" in output
