from tests.factories import create_employee
from tests.helpers.auth import (
    login_as_manager, login_as_sales, login_as_support
)


def test_employees_list_requires_login(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    from security import session_store
    import employees

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "session.json"
    )

    exit_code = employees.main(
        db_session=db_session,
        args=["list"],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "No active session" in output


def test_employees_list_as_manager(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import employees

    login_as_manager(monkeypatch, db_session, tmp_path)

    create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Support One",
        email="support.one@test.com",
        password="Password123!",
    )
    create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales One",
        email="sales.one@test.com",
        password="Password123!",
    )

    exit_code = employees.main(
        db_session=db_session,
        args=["list"],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Employees" in output
    assert "Support One" in output
    assert "Sales One" in output


def test_employees_list_as_sales_forbidden(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import employees

    login_as_sales(monkeypatch, db_session, tmp_path)

    exit_code = employees.main(
        db_session=db_session,
        args=["list"],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "employees.read_all" in output


def test_employees_get_as_manager(monkeypatch, db_session, tmp_path, capsys):
    import employees

    login_as_manager(monkeypatch, db_session, tmp_path)

    employee = create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Support Lookup",
        email="support.lookup@test.com",
        password="Password123!",
    )

    exit_code = employees.main(
        db_session=db_session,
        args=["get", "--employee-id", employee.employee_id],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Employee" in output
    assert "Support Lookup" in output
    assert "support.lookup@test.com" in output


def test_employees_create_as_manager(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import employees

    login_as_manager(monkeypatch, db_session, tmp_path)

    exit_code = employees.main(
        db_session=db_session,
        args=[
            "create",
            "--full-name", "New Support",
            "--email", "new.support@test.com",
            "--password", "Password123!",
            "--role", "support",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Employee created" in output
    assert "New Support" in output


def test_employees_create_as_sales_forbidden(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import employees

    login_as_sales(monkeypatch, db_session, tmp_path)

    exit_code = employees.main(
        db_session=db_session,
        args=[
            "create",
            "--full-name", "Forbidden Support",
            "--email", "forbidden.support@test.com",
            "--password", "Password123!",
            "--role", "support",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "employees.create" in output


def test_employees_create_rejects_duplicate_email(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import employees

    login_as_manager(monkeypatch, db_session, tmp_path)

    create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Existing Support",
        email="existing.support@test.com",
        password="Password123!",
    )

    exit_code = employees.main(
        db_session=db_session,
        args=[
            "create",
            "--full-name", "Other Support",
            "--email", "existing.support@test.com",
            "--password", "Password123!",
            "--role", "support",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "Employee already exists" in output


def test_employees_update_as_manager(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import employees

    login_as_manager(monkeypatch, db_session, tmp_path)

    employee = create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Support Before",
        email="support.before@test.com",
        password="Password123!",
    )

    exit_code = employees.main(
        db_session=db_session,
        args=[
            "update",
            "--employee-id", employee.employee_id,
            "--full-name", "Support After",
            "--email", "support.after@test.com",
            "--password", "Password123!",
            "--role", "commercial",
            "--is-active", "false",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Employee updated" in output
    assert "Support After" in output


def test_employees_update_as_sales_forbidden(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import employees

    login_as_sales(monkeypatch, db_session, tmp_path)

    employee = create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Support Target",
        email="support.target@test.com",
        password="Password123!",
    )

    exit_code = employees.main(
        db_session=db_session,
        args=[
            "update",
            "--employee-id", employee.employee_id,
            "--full-name", "Illegal Update",
            "--email", "illegal.update@test.com",
            "--password", "Password123!",
            "--role", "support",
            "--is-active", "true",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "employees.update" in output


def test_employees_update_rejects_duplicate_email(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import employees

    login_as_manager(monkeypatch, db_session, tmp_path)

    employee_1 = create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Employee One",
        email="employee.one@test.com",
        password="Password123!",
    )
    employee_2 = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Employee Two",
        email="employee.two@test.com",
        password="Password123!",
    )

    exit_code = employees.main(
        db_session=db_session,
        args=[
            "update",
            "--employee-id", employee_2.employee_id,
            "--full-name", "Employee Two Updated",
            "--email", employee_1.email,
            "--password", "Password123!",
            "--role", "commercial",
            "--is-active", "true",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "Employee already exists" in output


def test_employees_delete_as_manager(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import employees

    login_as_manager(monkeypatch, db_session, tmp_path)

    employee = create_employee(
        db_session=db_session,
        role_name="support",
        full_name="Support Delete",
        email="support.delete@test.com",
        password="Password123!",
    )

    exit_code = employees.main(
        db_session=db_session,
        args=[
            "delete",
            "--employee-id", employee.employee_id,
            "--yes",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code == 0
    assert "Employee deleted" in output


def test_employees_delete_as_support_forbidden(
        monkeypatch,
        db_session,
        tmp_path,
        capsys
):
    import employees

    login_as_support(monkeypatch, db_session, tmp_path)

    employee = create_employee(
        db_session=db_session,
        role_name="commercial",
        full_name="Sales Delete Target",
        email="sales.delete.target@test.com",
        password="Password123!",
    )

    exit_code = employees.main(
        db_session=db_session,
        args=[
            "delete",
            "--employee-id", employee.employee_id,
            "--yes",
        ],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err

    assert exit_code != 0
    assert "employees.delete" in output
