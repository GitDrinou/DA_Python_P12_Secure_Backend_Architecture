import click
from cli.printers import print_collection, print_row, print_success
from cli.verificators import run_click_app, require_permission
from security.permissions import (
    PERM_EMPLOYEES_READ_ALL, PERM_EMPLOYEES_CREATE, PERM_EMPLOYEES_UPDATE,
    PERM_EMPLOYEES_DELETE, ROLE_ADMIN, ROLE_MANAGEMENT, ROLE_SALES,
    ROLE_SUPPORT,
)
from services.employee_service import EmployeeService


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
@click.option("--employee-id", prompt=True, required=True)
@click.pass_context
def get_employee(ctx, employee_id):
    require_permission(ctx, PERM_EMPLOYEES_READ_ALL)
    service = EmployeeService(ctx.obj["db_session"])
    employee = service.get_employee(employee_id)
    print_row(employee_to_dict(employee), title="Employee")


@cli.command("create", help="Create an employee.")
@click.option("--full-name", prompt=True, required=True)
@click.option("--email", prompt=True, required=True)
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    required=True,
)
@click.option(
    "--role",
    "role_name",
    type=ROLE_CHOICES,
    prompt=True,
    required=True
)
@click.option(
    "--inactive",
    is_flag=True,
    default=False,
    help="Create employee as inactive."
)
@click.pass_context
def create_employee(ctx, full_name, email, password, role_name, inactive):
    current_employee = require_permission(ctx, PERM_EMPLOYEES_CREATE)
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
@click.option("--employee-id", prompt=True, required=True)
@click.option("--full-name", required=False)
@click.option("--email", required=False)
@click.option("--password", required=False, hide_input=True)
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
    service = EmployeeService(ctx.obj["db_session"])
    current = service.get_employee(employee_id)

    if full_name is None:
        full_name = click.prompt(
            "Full name",
            default=current.full_name,
            show_default=True
        )

    if email is None:
        email = click.prompt(
            "Email",
            default=current.email,
            show_default=True
        )

    if password is None:
        change_password = click.confirm("Change password?", default=False)
        if change_password:
            password = click.prompt(
                "New password",
                hide_input=True,
                confirmation_prompt=True,
            )

    if role_name is None:
        role_name = click.prompt(
            "Role",
            type=ROLE_CHOICES,
            default=current.role.name,
            show_default=True,
        )

    if is_active is None:
        is_active = "true" if current.is_active else "false"
        is_active = click.prompt(
            "Is active",
            type=click.Choice(["true", "false"]),
            default=is_active,
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
@click.option("--employee-id", prompt=True, required=True)
@click.confirmation_option(
    prompt="Do you really want to delete this employee ?"
)
@click.pass_context
def delete_employee(ctx, employee_id):
    current_employee = require_permission(ctx, PERM_EMPLOYEES_DELETE)
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


if __name__ == "__main__":
    raise SystemExit(main())
