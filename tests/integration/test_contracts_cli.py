from tests.factories import create_employee, create_customer, create_contract
from tests.helpers.auth import (
    login_as_manager, login_as_sales, login_as_support
)


def test_contracts_list_requires_login(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    from security import session_store
    import contracts

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    exit_code = contracts.main(
        db_session=db_session,
        args=["list"],
    )
    output = capsys.readouterr().out

    assert exit_code != 0
    assert "No active session" in output


def test_contracts_create_as_manager(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import contracts

    login_as_manager(monkeypatch, db_session, tmp_path)

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

    exit_code = contracts.main(
        db_session=db_session,
        args=[
            "create",
            "--customer-id", customer.customer_id,
            "--total-amount", "1500",
            "--remaining-amount", "1500",
            "--is-signed", "false",
        ],
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Contract created" in output


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

    exit_code = contracts.main(
        db_session=db_session,
        args=[
            "create",
            "--customer-id", customer.customer_id,
            "--total-amount", "1000",
            "--remaining-amount", "1000",
            "--is-signed", "false",
        ],
    )
    output = capsys.readouterr().out

    assert exit_code != 0
    assert "contracts.create_all" in output


def test_contracts_update_as_manager(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
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
        total_amount="2000.00",
        remaining_amount="2000.00",
    )

    exit_code = contracts.main(
        db_session=db_session,
        args=[
            "update",
            "--contract-id", contract.contract_id,
            "--total-amount", "2000",
            "--remaining-amount", "500",
            "--is-signed", "true",
        ],
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Contract updated" in output


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
        total_amount="1800.00",
        remaining_amount="900.00",
    )

    exit_code = contracts.main(
        db_session=db_session,
        args=[
            "update",
            "--contract-id", contract.contract_id,
            "--total-amount", "1800",
            "--remaining-amount", "300",
            "--is-signed", "true",
        ],
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Contract updated" in output


def test_contracts_update_as_sales_on_other_sales_customer_unauthorized(
    monkeypatch,
    db_session,
    tmp_path,
    capsys,
):
    import contracts

    login_as_sales(monkeypatch, db_session, tmp_path)

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
        total_amount="2500.00",
        remaining_amount="1000.00",
    )

    exit_code = contracts.main(
        db_session=db_session,
        args=[
            "update",
            "--contract-id", contract.contract_id,
            "--remaining-amount", "100",
            "--total-amount", "2500",
            "--is-signed", "false",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "You are not allowed to update contract" in output


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
        total_amount="1200.00",
        remaining_amount="1200.00",
    )

    exit_code = contracts.main(
        db_session=db_session,
        args=[
            "update",
            "--contract-id", contract.contract_id,
            "--remaining-amount", "800",
            "--total-amount", "1200",
            "--is-signed", "false",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "You are not allowed to update contract" in output


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
        total_amount="1000.00",
        remaining_amount="1000.00",
        is_signed=False,
    )

    exit_code = contracts.main(
        db_session=db_session,
        args=["list", "--unsigned-or-unpaid"],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Unsigned or unpaid contracts" in output
