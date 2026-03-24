import argparse
from cli.printers import print_collection, print_success, print_row
from cli.verificators import permission_required, handle_cli_errors
from database.session import SessionLocal
from security.permissions import PERM_CUSTOMERS_READ_ALL, \
    PERM_CUSTOMERS_CREATE_OWNED, PERM_CUSTOMERS_UPDATE_OWNED, \
    PERM_CUSTOMERS_DELETE_OWNED
from services.customer_service import CustomerService


def build_parser():
    parser = argparse.ArgumentParser(prog="customers.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List all customers")

    get_parser = subparsers.add_parser("get", help="Get customer details")
    get_parser.add_argument("--id", required=True)

    create_parser = subparsers.add_parser(
        "create",
        help="Create a new customer"
    )
    create_parser.add_argument("--full-name", required=True)
    create_parser.add_argument("--email", required=True)
    create_parser.add_argument("--phone", required=True)
    create_parser.add_argument("--company-name", required=True)
    create_parser.add_argument("--sales-id", required=True)

    update_parser = subparsers.add_parser(
        "update",
        help="Update a customer"
    )
    update_parser.add_argument("--id", required=True)
    update_parser.add_argument("--full-name")
    update_parser.add_argument("--email")
    update_parser.add_argument("--phone")
    update_parser.add_argument("--company-name")
    update_parser.add_argument("--sales-id")

    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a customer"
    )
    delete_parser.add_argument("--id", required=True)

    return parser


def customer_to_dict(customer):
    return {
        "customer_id": customer.customer_id,
        "full_name": customer.full_name,
        "email": customer.email,
        "phone": customer.phone,
        "company_name": customer.company_name,
        "sales_id": customer.sales_id,
    }


@permission_required(PERM_CUSTOMERS_READ_ALL)
def handle_list(current_employee=None, db_session=None):
    service = CustomerService(db_session)
    customers = service.list_customers()
    print_collection([customer_to_dict(cust) for cust in customers])
    return 0


@permission_required(PERM_CUSTOMERS_READ_ALL)
def handle_get(customer_id, current_employee=None, db_session=None):
    service = CustomerService(db_session)
    customer = service.get_customer(customer_id)
    print_row(customer_to_dict(customer))
    return 0


@permission_required(PERM_CUSTOMERS_CREATE_OWNED)
def handle_create(args, current_employee=None, db_session=None):
    service = CustomerService(db_session)
    customer = service.create_customer(
        full_name=args.full_name,
        email=args.email,
        phone=args.phone,
        company_name=args.company_name,
        current_employee=current_employee
    )
    print_success(
        f"Customer created: {customer.full_name} (id: {customer.customer_id})"
    )
    return 0


@permission_required(PERM_CUSTOMERS_UPDATE_OWNED)
def handle_update(args, current_employee=None, db_session=None):
    service = CustomerService(db_session)
    customer = service.update_customer(
        customer_id=args.customer_id,
        full_name=args.full_name,
        email=args.email,
        phone=args.phone,
        company_name=args.company_name,
        current_employee=current_employee
    )
    print_success(
        f"Customer updated: {customer.full_name} (id: {customer.customer_id})"
    )
    return 0


@permission_required(PERM_CUSTOMERS_DELETE_OWNED)
def handle_delete(customer_id, current_employee=None, db_session=None):
    service = CustomerService(db_session)
    service.delete_customer(current_employee, customer_id)
    print_success("Customer deleted")
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
            return handle_get(args.id, db_session=db_session)

        if args.command == "create":
            return handle_create(args, db_session=db_session)

        if args.command == "update":
            return handle_update(args, db_session=db_session)

        if args.command == "delete":
            return handle_delete(args.id, db_session=db_session)

        return 1
    finally:
        if created_session:
            db_session.close()


if __name__ == "__main__":
    raise SystemExit(main())
