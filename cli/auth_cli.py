from security import get_authenticated_employee
from security.auth_service import login
from security.session_store import save_session


def authenticate_employee(db_session, email, password):
    auth_result = login(db_session, email, password)
    save_session(
        auth_result["access_token"],
        auth_result["refresh_token"],
    )

    employee = get_authenticated_employee(
        db_session,
        auth_result["access_token"],
    )

    return employee

