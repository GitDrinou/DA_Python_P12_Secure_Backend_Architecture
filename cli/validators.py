import click
from cli.context import get_current_employee, CliAuthenticationError
from cli.printers import print_forbidden, print_error
from database.session import SessionLocal
from observability import get_application_logger, init_observability, \
    flush_observability
from security import has_permission, AuthorizationError


logger = get_application_logger()


def get_db_session(ctx):
    return ctx.obj["db_session"]


def require_login(ctx):
    return get_current_employee(db_session=get_db_session(ctx))


def require_permission(ctx, permission_code):
    employee = require_login(ctx)

    if not has_permission(employee, permission_code):
        raise AuthorizationError(
            f"You don't have permission: {permission_code}"
        )

    return employee


def run_click_app(app, db_session=None, args=None, prog_name=None):
    created_session = False

    if db_session is None:
        db_session = SessionLocal()
        created_session = True

    init_observability()

    try:
        app.main(
            args=args,
            prog_name=prog_name,
            obj={"db_session": db_session},
            standalone_mode=False,
        )
        return 0
    except CliAuthenticationError as exception:
        print_forbidden(str(exception))
        return 1
    except AuthorizationError as exception:
        print_forbidden(str(exception))
        return 1
    except click.ClickException as exception:
        print_error(exception.format_message())
        return 1
    except ValueError as exception:
        print_error(str(exception))
        return 1
    except Exception as exception:
        logger.exception("Unhandled exception in CLI command")
        print_error(f"Unexpected error: {exception}")
        return 1
    finally:
        flush_observability(timeout=2.0)
        if created_session:
            db_session.close()
