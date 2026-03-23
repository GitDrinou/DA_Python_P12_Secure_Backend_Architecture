from database.session import SessionLocal
from security import AuthorizationError, get_authenticated_employee
from security.session_store import load_session


class CliAuthenticationError(Exception):
    pass


def get_current_session_tokens():
    """ Return session tokens """
    session_data = load_session()
    if not session_data:
        raise CliAuthenticationError(
            "No active session. Please login with: >> epic_events.py login <<"
        )
    return session_data


def get_current_employee(db_session=None):
    """ Return employee information """
    session_data = get_current_session_tokens()
    access_token = session_data["access_token"]

    if not access_token:
        raise CliAuthenticationError(
            "Invalide session. Please relogin with: >> epic_events.py login <<"
        )

    created_session = False
    if db_session is None:
        db_session = SessionLocal()
        created_session = True

    try:
        employee = get_authenticated_employee(db_session, access_token)
        return employee
    except AuthorizationError as exception:
        raise CliAuthenticationError(
            f"Expired session or invalid session: {exception}"
        ) from exception
    finally:
        if created_session:
            db_session.close()
