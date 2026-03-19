from cli.app import run_main_menu
from cli.auth_cli import authenticate_employee
from database.session import SessionLocal
from security import AuthorizationError


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def main():
    db_session = SessionLocal()

    try:
        email = input("Email: ").strip()
        password = input("Mot de passe: ").strip()

        employee = authenticate_employee(db_session, email, password)
        run_main_menu(employee)

    except AuthorizationError as exc:
        print(f"Erreur d'authentification: {exc}")
    finally:
        db_session.close()


if __name__ == '__main__':
    main()
