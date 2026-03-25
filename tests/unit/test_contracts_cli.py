import sys

from security.rbac import seed_rbac
from tests.factories import create_employee, create_customer, create_contract


def login_as_manager(monkeypatch, db_session, tmp_path):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json",
    )

    seed_rbac(db_session)
    manager = create_employee(
        db_session=db_session,
        role_name="gestion",
        full_name="Manager Test",
        email="manager.contracts@test.com",
        password="Password123!",
    )
    db_session.flush()
    db_session.commit()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "epic_events.py",
            "login",
            "--email",
            manager.email,
            "--password",
            "Password123!",
        ],
    )
    epic_events.main(db_session=db_session)
    return manager


def login_as_sales(monkeypatch, db_session, tmp_path):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json",
    )

    seed_rbac(db_session)
    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales Test",
        email="sales.contracts@test.com",
        password="Password123!",
    )
    db_session.flush()
    db_session.commit()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "epic_events.py",
            "login",
            "--email",
            sales.email,
            "--password",
            "Password123!",
        ],
    )
    epic_events.main(db_session=db_session)
    return sales


def login_as_support(monkeypatch, db_session, tmp_path):
    from security import session_store
    import epic_events

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json",
    )

    seed_rbac(db_session)
    support = create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Support Test",
        email="support.contracts@test.com",
        password="Password123!",
    )
    db_session.flush()
    db_session.commit()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "epic_events.py",
            "login",
            "--email",
            support.email,
            "--password",
            "Password123!",
        ],
    )
    epic_events.main(db_session=db_session)
    return support


def test_contracts_list_requires_login(monkeypatch, capsys, tmp_path):
    from security import session_store
    import contracts

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json",
    )
    monkeypatch.setattr(sys, "argv", ["contracts.py", "list"])

    exit_code = contracts.main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert (
        "[FORBIDDEN] No active session. "
        "Please login with: >> epic_events.py login <<"
    ) in output


def test_contracts_create_as_manager(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import contracts

    manager = login_as_manager(monkeypatch, db_session, tmp_path)

    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales Owner",
        email="sales.owner@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.create.contract@test.com",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "contracts.py",
            "create",
            "--customer-id", customer.customer_id,
            "--total-amount", "1500.00",
            "--remaining-amount", "1500.00",
            "--is-signed", "false",
        ],
    )

    exit_code = contracts.main(db_session=db_session)
    output = capsys.readouterr().out

    assert manager is not None
    assert exit_code == 0
    assert "[SUCCESS] Contract created" in output


def test_contracts_create_as_sales_unauthorized(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import contracts

    sales = login_as_sales(monkeypatch, db_session, tmp_path)

    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.sales.contract@test.com",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "contracts.py",
            "create",
            "--customer-id", customer.customer_id,
            "--total-amount", "1000.00",
            "--remaining-amount", "1000.00",
            "--is-signed", "false",
        ],
    )

    exit_code = contracts.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert ("[UNEXPECTED] You don't have permission: contracts.create_all" in
            output)


def test_contracts_update_as_manager(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import contracts

    login_as_manager(monkeypatch, db_session, tmp_path)

    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales Owner",
        email="sales.update.manager@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.update.manager@test.com",
    )
    contract = create_contract(
        db_session=db_session,
        customer=customer,
        total="2000.00",
        remaining="2000.00",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "contracts.py",
            "update",
            "--contract-id", contract.contract_id,
            "--remaining-amount", "500.00",
            "--is-signed", "true",
        ],
    )

    exit_code = contracts.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "[SUCCESS] Contract updated" in output


def test_contracts_update_as_sales_on_owned_customer(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import contracts

    sales = login_as_sales(monkeypatch, db_session, tmp_path)

    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.owned.contract@test.com",
    )
    contract = create_contract(
        db_session=db_session,
        customer=customer,
        total="1800.00",
        remaining="900.00",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "contracts.py",
            "update",
            "--contract-id", contract.contract_id,
            "--remaining-amount", "300.00",
            "--is-signed", "true",
        ],
    )

    exit_code = contracts.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "[SUCCESS] Contract updated" in output


def test_contracts_update_as_sales_on_other_sales_customer_unauthorized(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import contracts

    alice = login_as_sales(monkeypatch, db_session, tmp_path)

    bob = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Other Sales",
        email="other.sales.contract@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=bob,
        email="customer.other.sales.contract@test.com",
    )
    contract = create_contract(
        db_session=db_session,
        customer=customer,
        total="2500.00",
        remaining="1000.00",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "contracts.py",
            "update",
            "--contract-id", contract.contract_id,
            "--remaining-amount", "100.00",
        ],
    )

    exit_code = contracts.main(db_session=db_session)
    output = capsys.readouterr().out

    assert alice is not None
    assert exit_code == 1
    assert "[ERROR] You are not allowed to update this contract" in output


def test_contracts_update_as_support_unauthorized(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import contracts

    login_as_support(monkeypatch, db_session, tmp_path)

    sales = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales Owner",
        email="sales.support.contract@test.com",
        password="Password123!",
    )
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.support.contract@test.com",
    )
    contract = create_contract(
        db_session=db_session,
        customer=customer,
        total="1200.00",
        remaining="1200.00",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "contracts.py",
            "update",
            "--contract-id", contract.contract_id,
            "--remaining-amount", "800.00",
        ],
    )

    exit_code = contracts.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "[ERROR] You are not allowed to update this contract" in output


def test_contracts_list_unsigned_or_unpaid_as_sales(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import contracts

    sales = login_as_sales(monkeypatch, db_session, tmp_path)

    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.filter.contract@test.com",
    )
    create_contract(
        db_session=db_session,
        customer=customer,
        total="1000.00",
        remaining="1000.00",
        is_signed=False,
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "contracts.py",
            "list",
            "--unsigned-or-unpaid",
        ],
    )

    exit_code = contracts.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 0, output
    assert "contract_id" in output


def test_contracts_list_unsigned_or_unpaid_as_support_unauthorized(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import contracts

    login_as_support(monkeypatch, db_session, tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "contracts.py",
            "list",
            "--unsigned-or-unpaid",
        ],
    )

    exit_code = contracts.main(db_session=db_session)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert (
        "[UNEXPECTED] You don't have permission: "
        "contracts.filter_unsigned_or_unpaid"
    ) in output
