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


def get_current_employee():
    """ Return employee information """
    session_data = get_current_session_tokens()
    access_token = session_data["access_token"]

    if not access_token:
        raise CliAuthenticationError(
            "Invalide session. Please relogin with: >> epic_events.py login <<"
        )

    db_session = SessionLocal()
    try:
        employee = get_authenticated_employee(db_session, access_token)
        db_session.expunge(employee)
        return employee
    except AuthorizationError as exception:
        raise CliAuthenticationError(
            f"Expired session or invalid session: {exception}"
        ) from exception
    finally:
        db_session.close()
