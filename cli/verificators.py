from functools import wraps
from cli.context import get_current_employee, CliAuthenticationError
from security import has_permission, AuthorizationError


def login_required(func):
    """ Decorator to check if the user is logged in. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        employee = get_current_employee()
        return func(*args, current_employee=employee, **kwargs)
    return wrapper


def permission_required(permission_code):
    """ Decorator to check if the user has permission to the requested
    resource. """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            employee = get_current_employee()

            if not has_permission(employee, permission_code):
                raise AuthorizationError(
                    f"You don't have permission: {permission_code}"
                )
            return func(*args, current_employee=employee, **kwargs)
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
