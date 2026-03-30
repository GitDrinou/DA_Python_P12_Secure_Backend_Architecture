import argparse

from cli.printers import print_collection, print_success, print_row
from cli.verificators import permission_required, login_required, \
    handle_cli_errors
from database.session import SessionLocal
from security import has_permission, AuthorizationError
from security.permissions import PERM_CONTRACTS_READ_ALL, \
    PERM_CONTRACTS_FILTER_UNSIGNED_OR_UNPAID, PERM_CONTRACTS_CREATE_ALL
from services.contract_service import ContractService


def build_parser():
    parser = argparse.ArgumentParser(prog="contracts.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list contracts")
    list_parser.add_argument(
        "--unsigned-or-unpaid",
        action="store_true",
        help="Filter unsigned or unpaid contracts",
    )

    get_parser = subparsers.add_parser("get", help="Get contract details")
    get_parser.add_argument("--contract-id", required=True)

    create_parser = subparsers.add_parser(
        "create",
        help="Create a new contract"
    )
    create_parser.add_argument("--customer-id", required=True)
    create_parser.add_argument("--total-amount", required=True)
    create_parser.add_argument("--remaining-amount", required=True)
    create_parser.add_argument("--is-signed", choices=["true", "false"])

    update_parser = subparsers.add_parser(
        "update",
        help="Update contract details"
    )
    update_parser.add_argument("--contract-id", required=True)
    update_parser.add_argument("--total-amount")
    update_parser.add_argument("--remaining-amount")
    update_parser.add_argument("--is-signed", choices=["true", "false"])

    return parser


def contract_to_dict(contract):
    return {
        "contract_id": contract.contract_id,
        "customer_id": contract.customers_id,
        "customer_name": contract.customer.full_name if contract.customer
        else None,
        "sales_id": contract.customer.sales_id if contract.customer else None,
        "total_amount": contract.total_amount,
        "remaining_amount": contract.remaining_amount,
        "is_signed": contract.is_signed,
    }


@permission_required(PERM_CONTRACTS_READ_ALL)
def handle_list(args, current_employee=None, db_session=None):
    if (
        args.unsigned_or_unpaid
        and not has_permission(
            current_employee,
            PERM_CONTRACTS_FILTER_UNSIGNED_OR_UNPAID,
        )
    ):
        raise AuthorizationError(
            f"You don't have permission: "
            f"{PERM_CONTRACTS_FILTER_UNSIGNED_OR_UNPAID}"
        )

    service = ContractService(db_session)
    contracts = service.list_contracts()
    print_collection([contract_to_dict(contract) for contract in contracts])
    return 0


@permission_required(PERM_CONTRACTS_READ_ALL)
def handle_get(contract_id, db_session=None):
    service = ContractService(db_session)
    contract = service.get_contract(contract_id)
    print_row(contract_to_dict(contract))
    return 0


@permission_required(PERM_CONTRACTS_CREATE_ALL)
def handle_create(args, current_employee=None, db_session=None):
    service = ContractService(db_session)
    is_signed = None
    if args.is_signed is not None:
        is_signed = args.is_signed == "true"

    contract = service.create_contract(
        current_employee=current_employee,
        customer_id=args.customer_id,
        total_amount=args.total_amount,
        remaining_amount=args.remaining_amount,
        is_signed=is_signed,
    )
    print_success(
        f"Contract created: {contract.contract_id}"
        f" (customer: {contract.customers_id})"
    )
    return 0


@login_required
def handle_update(args, current_employee=None, db_session=None):
    service = ContractService(db_session)
    is_signed = None
    if args.is_signed is not None:
        is_signed = args.is_signed == "true"

    contract = service.update_contract(
        contract_id=args.contract_id,
        current_employee=current_employee,
        total_amount=args.total_amount,
        remaining_amount=args.remaining_amount,
        is_signed=is_signed,
    )
    print_success(f"Contract updated: {contract.contract_id}")
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
            return handle_list(args, db_session=db_session)

        if args.command == "get":
            return handle_get(args.contract_id, db_session=db_session)

        if args.command == "create":
            return handle_create(args, db_session=db_session)

        if args.command == "update":
            return handle_update(args, db_session=db_session)

        return 1
    finally:
        if created_session:
            db_session.close()


if __name__ == "__main__":
    raise SystemExit(main())
