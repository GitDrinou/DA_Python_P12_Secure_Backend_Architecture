import argparse
from cli.printers import print_success, print_info
from security import AuthenticationError
from security.auth_service import login
from security.session_store import save_session, clear_session
from database.session import SessionLocal
from cli.context import get_current_employee
from cli.verificators import handle_cli_errors


def build_parser():
    """ Build argument parser """
    parser = argparse.ArgumentParser(prog="epic_events.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    login_parser = subparsers.add_parser("login", help="User login")
    login_parser.add_argument("--email", required=True)
    login_parser.add_argument("--password", required=True)

    subparsers.add_parser("logout", help="User logour")
    subparsers.add_parser("whoami", help="Current user")

    return parser


@handle_cli_errors
def main(db_session=None):
    parser = build_parser()
    args = parser.parse_args()

    create_session = False
    if db_session is None:
        db_session = SessionLocal()
        create_session = True
    try:
        if args.command == "login":
            try:
                auth_result = login(db_session, args.email, args.password)
                save_session(
                    auth_result["access_token"],
                    auth_result["refresh_token"],
                )
                print_success("Successfully logged in")
                return 0
            except AuthenticationError as exc:
                print(f"[AUTH] {exc}")
                return 1

        if args.command == "logout":
            clear_session()
            print_success("Successfully logged out")
            return 0

        if args.command == "whoami":
            employee = get_current_employee(db_session=db_session)
            print_info("Connected user")
            print(f"id: {employee.employee_id}")
            print(f"name: {employee.full_name}")
            print(f"email: {employee.email}")
            print(f"role: {employee.role.name}")
            return 0

        return 1
    finally:
        if create_session:
            db_session.close()


if __name__ == '__main__':
    raise SystemExit(main())
