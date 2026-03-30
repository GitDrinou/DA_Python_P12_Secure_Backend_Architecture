import argparse
from cli.printers import print_collection, print_success, print_row
from cli.verificators import permission_required, handle_cli_errors
from database.session import SessionLocal
from security.permissions import PERM_EMPLOYEES_READ_ALL, \
    PERM_EMPLOYEES_CREATE, PERM_EMPLOYEES_UPDATE, PERM_EMPLOYEES_DELETE
from services.employee_service import EmployeeService


def build_parser():
    parser = argparse.ArgumentParser(prog="employees.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List employees")

    get_parser = subparsers.add_parser("get", help="Get employee details")
    get_parser.add_argument("--employee-id", required=True)

    create_parser = subparsers.add_parser(
        "create",
        help="Create a new employee"
    )
    create_parser.add_argument("--full-name", required=True)
    create_parser.add_argument("--email", required=True)
    create_parser.add_argument("--password", required=True)
    create_parser.add_argument("--role", required=True)
    create_parser.add_argument("--inactive", action="store_true")

    update_parser = subparsers.add_parser(
        "update",
        help="Update an employee"
    )
    update_parser.add_argument("--employee-id", required=True)
    update_parser.add_argument("--full-name")
    update_parser.add_argument("--email")
    update_parser.add_argument("--password")
    update_parser.add_argument("--role")
    update_parser.add_argument("--is-active", choices=["true", "false"])

    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete an employee"
    )
    delete_parser.add_argument("--employee-id", required=True)

    return parser


def employee_to_dict(employee):
    return {
        "employee_id": employee.employee_id,
        "full_name": employee.full_name,
        "email": employee.email,
        "role": employee.role.name if employee.role else None,
        "is_active": employee.is_active,
    }


@permission_required(PERM_EMPLOYEES_READ_ALL)
def handle_list(current_employee=None, db_session=None):
    service = EmployeeService(db_session)
    employees = service.list_employees()
    print_collection([employee_to_dict(emp) for emp in employees])
    return 0


@permission_required(PERM_EMPLOYEES_READ_ALL)
def handle_get(employee_id, current_employee=None, db_session=None):
    service = EmployeeService(db_session)
    employee = service.get_employee(employee_id)
    print_row(employee_to_dict(employee))
    return 0


@permission_required(PERM_EMPLOYEES_CREATE)
def handle_create(args, current_employee=None, db_session=None):
    service = EmployeeService(db_session)
    employee = service.create_employee(
        current_employee=current_employee,
        full_name=args.full_name,
        email=args.email,
        password=args.password,
        role_name=args.role,
        is_active=not args.inactive,
    )
    print_success(
        f"Employee created: {employee.full_name} (id:"
        f" {employee.employee_id})")
    return 0


@permission_required(PERM_EMPLOYEES_UPDATE)
def handle_update(args, current_employee=None, db_session=None):
    service = EmployeeService(db_session)
    is_active = None
    if args.is_active is not None:
        is_active = args.is_active == "true"

    employee = service.update_employee(
        current_employee=current_employee,
        employee_id=args.employee_id,
        full_name=args.full_name,
        email=args.email,
        password=args.password,
        role_name=args.role,
        is_active=is_active,
    )
    print_success(
        f"Employee updated: {employee.full_name}"
        f"(id: {employee.employee_id})"
    )
    return 0


@permission_required(PERM_EMPLOYEES_DELETE)
def handle_delete(employee_id, current_employee=None, db_session=None):
    service = EmployeeService(db_session)
    service.delete_employee(
        current_employee=current_employee,
        employee_id=employee_id
    )
    print_success("Employee deleted")
    return 0


@handle_cli_errors
def main(db_session=None):
    parser = build_parser()
    args = parser.parse_args()

    created_session = False
    if db_session is None:
        db_session = SessionLocal()
        created_session = True

    try:
        if args.command == "list":
            return handle_list(db_session=db_session)

        if args.command == "get":
            return handle_get(args.employee_id, db_session=db_session)

        if args.command == "create":
            return handle_create(args, db_session=db_session)

        if args.command == "update":
            return handle_update(args, db_session=db_session)

        if args.command == "delete":
            return handle_delete(args.employee_id, db_session=db_session)

        return 1
    finally:
        if created_session:
            db_session.close()


if __name__ == "__main__":
    raise SystemExit(main())
