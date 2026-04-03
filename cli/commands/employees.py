import click
from cli.printers import print_collection, print_row, print_success, \
    print_error
from cli.validators import run_click_app, require_permission
from security.permissions import (
    PERM_EMPLOYEES_READ_ALL, PERM_EMPLOYEES_CREATE, PERM_EMPLOYEES_UPDATE,
    PERM_EMPLOYEES_DELETE, ROLE_ADMIN, ROLE_MANAGEMENT, ROLE_SALES,
    ROLE_SUPPORT,
)
from services.employee_service import EmployeeService
from cli.interactions import prompt_if_missing, confirm_if_requested
from security.passwords import validate_password_strength


ROLE_CHOICES = click.Choice([
    ROLE_ADMIN,
    ROLE_MANAGEMENT,
    ROLE_SALES, ROLE_SUPPORT
])


def employee_to_dict(employee):
    return {
        "employee_id": employee.employee_id,
        "full_name": employee.full_name,
        "email": employee.email,
        "role": employee.role.name if employee.role else None,
        "is_active": employee.is_active,
    }


def validate_password_option(ctx, param, value):
    if value is None:
        return value

    try:
        validate_password_strength(value)
    except ValueError as exc:
        raise click.BadParameter(str(exc))

    return value


def prompt_password(label):
    while True:
        password = click.prompt(
            label,
            hide_input=True,
            confirmation_prompt=True,
        )
        try:
            validate_password_strength(password)
            return password
        except ValueError as exc:
            print_error(str(exc))


@click.group(help="Manage employees.")
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.command("list", help="List all employees.")
@click.pass_context
def list_employees(ctx):
    require_permission(ctx, PERM_EMPLOYEES_READ_ALL)
    service = EmployeeService(ctx.obj["db_session"])
    employees = service.list_employees()
    print_collection(
        [employee_to_dict(employee) for employee in employees],
        title="Employees",
    )


@cli.command("get", help="Display an employee.")
@click.option("--employee-id", required=False)
@click.pass_context
def get_employee(ctx, employee_id):
    require_permission(ctx, PERM_EMPLOYEES_READ_ALL)

    employee_id = prompt_if_missing(employee_id, "Employee id")

    service = EmployeeService(ctx.obj["db_session"])
    employee = service.get_employee(employee_id)
    print_row(employee_to_dict(employee), title="Employee")


@cli.command("create", help="Create an employee.")
@click.option("--full-name", required=False)
@click.option("--email", required=False)
@click.option(
    "--password",
    required=False,
    hide_input=True,
    callback=validate_password_option,
)
@click.option("--role", "role_name", type=ROLE_CHOICES, required=False)
@click.option(
    "--inactive",
    is_flag=True,
    default=False,
    help="Create employee as inactive."
)
@click.pass_context
def create_employee(ctx, full_name, email, password, role_name, inactive):
    current_employee = require_permission(ctx, PERM_EMPLOYEES_CREATE)

    full_name = prompt_if_missing(full_name, "Full name")
    email = prompt_if_missing(email, "Email")
    if password is None:
        password = prompt_password("Password")
    role_name = prompt_if_missing(role_name, "Role", type=ROLE_CHOICES)

    service = EmployeeService(ctx.obj["db_session"])
    employee = service.create_employee(
        current_employee=current_employee,
        full_name=full_name,
        email=email,
        password=password,
        role_name=role_name,
        is_active=not inactive,
    )
    print_success(
        f"Employee created: {employee.full_name} ({employee.employee_id})"
    )


@cli.command("update", help="Update an employee.")
@click.option("--employee-id", required=False)
@click.option("--full-name", required=False)
@click.option("--email", required=False)
@click.option(
    "--password",
    required=False,
    hide_input=True,
    callback=validate_password_option,
)
@click.option("--role", "role_name", type=ROLE_CHOICES, required=False)
@click.option(
    "--is-active",
    type=click.Choice(["true", "false"]),
    required=False
)
@click.pass_context
def update_employee(
        ctx,
        employee_id,
        full_name,
        email,
        password,
        role_name,
        is_active
):
    current_employee = require_permission(ctx, PERM_EMPLOYEES_UPDATE)

    employee_id = prompt_if_missing(employee_id, "Employee id")

    service = EmployeeService(ctx.obj["db_session"])
    current = service.get_employee(employee_id)

    full_name = prompt_if_missing(
        full_name,
        "Full name",
        default=current.full_name,
        show_default=True,
    )
    email = prompt_if_missing(
        email,
        "Email",
        default=current.email,
        show_default=True,
    )

    if password is None:
        change_password = click.confirm("Change password?", default=False)
        if change_password:
            password = prompt_password("New password")

    role_name = prompt_if_missing(
        role_name,
        "Role",
        type=ROLE_CHOICES,
        default=current.role.name,
        show_default=True,
    )

    if is_active is None:
        is_active = click.prompt(
            "Is active",
            type=click.Choice(["true", "false"]),
            default="true" if current.is_active else "false",
            show_default=True,
        )

    employee = service.update_employee(
        current_employee=current_employee,
        employee_id=employee_id,
        full_name=full_name,
        email=email,
        password=password,
        role_name=role_name,
        is_active=(is_active == "true"),
    )
    print_success(
        f"Employee updated: {employee.full_name} ({employee.employee_id})"
    )


@cli.command("delete", help="Delete an employee.")
@click.option("--employee-id", required=False)
@click.option(
    "--yes",
    is_flag=True,
    help="Confirm deletion without interactive prompt.",
)
@click.pass_context
def delete_employee(ctx, employee_id, yes):
    current_employee = require_permission(ctx, PERM_EMPLOYEES_DELETE)

    employee_id = prompt_if_missing(employee_id, "Employee id")
    confirm_if_requested(yes, "Do you really want to delete this employee ?")

    service = EmployeeService(ctx.obj["db_session"])
    service.delete_employee(
        current_employee=current_employee,
        employee_id=employee_id,
    )
    print_success("Employee deleted")


def main(db_session=None, args=None):
    return run_click_app(
        cli,
        db_session=db_session,
        args=args,
        prog_name="employees.py",
    )


employees_group: click.Group = cli
