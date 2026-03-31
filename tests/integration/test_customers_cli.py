from tests.helpers.auth import login_as_sales


def test_customers_list_requires_login(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    from security import session_store
    import customers

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    exit_code = customers.main(
        db_session=db_session,
        args=["list"],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "No active session" in output


def test_customers_create_as_sales(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import customers

    login_as_sales(monkeypatch, db_session, tmp_path)

    exit_code = customers.main(
        db_session=db_session,
        args=[
            "create",
            "--full-name", "New Customer",
            "--email", "new.customer@test.com",
            "--phone", "123-456-789",
            "--company-name", "Customer Test SA",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Customer created" in output


def test_customers_update_as_sales(monkeypatch, db_session, tmp_path, capsys):
    import customers
    from tests.factories import create_customer

    sales = login_as_sales(monkeypatch, db_session, tmp_path)
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        full_name="Customer Before",
        email="customer.before@test.com",
    )

    exit_code = customers.main(
        db_session=db_session,
        args=[
            "update",
            "--customer-id", customer.customer_id,
            "--full-name", "Customer After",
            "--email", "customer.after@test.com",
            "--phone", "0102030405",
            "--company-name", "Updated Company",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Customer updated" in output


def test_customers_delete_as_sales(monkeypatch, db_session, tmp_path, capsys):
    import customers
    from tests.factories import create_customer

    sales = login_as_sales(monkeypatch, db_session, tmp_path)
    customer = create_customer(
        db_session=db_session,
        sales_employee=sales,
        email="customer.delete@test.com",
    )

    exit_code = customers.main(
        db_session=db_session,
        args=[
            "delete",
            "--customer-id", customer.customer_id,
            "--yes",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Customer deleted" in output
