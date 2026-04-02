import click
from cli.printers import print_success, print_kv_panel
from cli.validators import require_login, run_click_app
from security import AuthenticationError
from security.auth_service import login
from security.session_store import save_session, clear_session

from cli.commands.contracts import contracts_group
from cli.commands.customers import customers_group
from cli.commands.employees import employees_group
from cli.commands.events import events_group
from cli.commands.permissions import permissions_group


@click.group(help="Main CLI for EPIC Events CRM")
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.command("login", help="Login user and store session tokens.")
@click.option("--email", prompt=True, help="User email.")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    help="User password.",
)
@click.pass_context
def login_command(ctx, email, password):
    db_session = ctx.obj["db_session"]

    try:
        auth_result = login(db_session, email, password)
    except AuthenticationError as exc:
        raise click.ClickException(str(exc)) from exc

    save_session(
        auth_result["access_token"],
        auth_result["refresh_token"],
    )
    print_success("Successfully logged in")


@cli.command("logout", help="Remove current session.")
def logout_command():
    clear_session()
    print_success("Successfully logged out")


@cli.command("whoami", help="Display current authenticated user details.")
@click.pass_context
def whoami_command(ctx):
    employee = require_login(ctx)
    print_kv_panel(
        "Connected user",
        {
            "employee_id": employee.employee_id,
            "full_name": employee.full_name,
            "email": employee.email,
            "role": employee.role.name if employee.role else None,
        },
    )


cli.add_command(employees_group, name="employees")
cli.add_command(customers_group, name="customers")
cli.add_command(contracts_group, name="contracts")
cli.add_command(events_group, name="events")
cli.add_command(permissions_group, name="permissions")


def main(db_session=None, args=None):
    return run_click_app(
        cli,
        db_session=db_session,
        args=args,
        prog_name="epic_events.py",
    )
