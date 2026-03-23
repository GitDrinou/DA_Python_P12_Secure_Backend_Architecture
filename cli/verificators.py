from functools import wraps
from cli.context import get_current_employee, CliAuthenticationError
from security import has_permission, AuthorizationError


def login_required(func):
    """ Decorator to check if the user is logged in. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        db_session = kwargs.get("db_session")
        employee = get_current_employee(db_session=db_session)
        kwargs["current_employee"] = employee
        return func(*args, **kwargs)
    return wrapper


def permission_required(permission_code):
    """ Decorator to check if the user has permission to the requested
    resource. """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            db_session = kwargs.get("db_session")
            employee = get_current_employee(db_session=db_session)

            if not has_permission(employee, permission_code):
                raise AuthorizationError(
                    f"You don't have permission: {permission_code}"
                )
            kwargs["current_employee"] = employee
            return func(*args, **kwargs)
        return wrapper
    return decorator


def handle_cli_errors(func):
    """ Decorator to handle CLI errors. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CliAuthenticationError as e:
            print(f"[FORBIDDEN] {e}")
            return 1
        except ValueError as e:
            print(f"[ERROR] {e}")
            return 1
        except Exception as e:
            print(f"[UNEXPECTED] {e}")
            return 1
    return wrapper
