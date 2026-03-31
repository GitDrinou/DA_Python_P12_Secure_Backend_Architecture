import click
from cli.printers import print_collection, print_row, print_success
from cli.verificators import run_click_app, require_login, require_permission
from security.permissions import (
    PERM_CONTRACTS_READ_ALL, PERM_CONTRACTS_FILTER_UNSIGNED_OR_UNPAID,
    PERM_CONTRACTS_CREATE_ALL,
)
from services.contract_service import ContractService


def contract_to_dict(contract):
    return {
        "contract_id": contract.contract_id,
        "customer_id": contract.customers_id,
        "customer_name": contract.customer.full_name if contract.customer
        else None,
        "sales_id": contract.customer.sales_id if contract.customer else None,
        "sales_name": contract.customer.sales.full_name if contract.customer
        else None,
        "total_amount": contract.total_amount,
        "remaining_amount": contract.remaining_amount,
        "is_signed": contract.is_signed,
    }


@click.group(help="Manage contracts.")
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.command("list", help="List all contracts.")
@click.option("--unsigned-or-unpaid", is_flag=True, default=False)
@click.pass_context
def list_contracts(ctx, unsigned_or_unpaid):
    current_employee = require_permission(ctx, PERM_CONTRACTS_READ_ALL)
    service = ContractService(ctx.obj["db_session"])

    if unsigned_or_unpaid:
        require_permission(ctx, PERM_CONTRACTS_FILTER_UNSIGNED_OR_UNPAID)
        contracts = service.list_unsigned_or_unpaid_contracts(current_employee)
        print_collection(
            [contract_to_dict(contract) for contract in contracts],
            title="Unsigned or unpaid contracts",
        )
        return

    contracts = service.list_contracts()
    print_collection(
        [contract_to_dict(contract) for contract in contracts],
        title="Contracts",
    )


@cli.command("get", help="Display a contract.")
@click.option("--contract-id", prompt=True, required=True)
@click.pass_context
def get_contract(ctx, contract_id):
    require_permission(ctx, PERM_CONTRACTS_READ_ALL)
    service = ContractService(ctx.obj["db_session"])
    contract = service.get_contract(contract_id)
    print_row(contract_to_dict(contract), title="Contract")


@cli.command("create", help="Create a contract.")
@click.option("--customer-id", prompt=True, required=True)
@click.option("--total-amount", prompt=True, required=True, type=float)
@click.option("--remaining-amount", prompt=True, required=True, type=float)
@click.option(
    "--is-signed",
    type=click.Choice(["true", "false"]),
    prompt=True,
    required=False,
    default="false",
    show_default=True,
)
@click.pass_context
def create_contract(
        ctx,
        customer_id,
        total_amount,
        remaining_amount,
        is_signed
):
    current_employee = require_permission(ctx, PERM_CONTRACTS_CREATE_ALL)
    service = ContractService(ctx.obj["db_session"])
    contract = service.create_contract(
        current_employee=current_employee,
        customer_id=customer_id,
        total_amount=total_amount,
        remaining_amount=remaining_amount,
        is_signed=(is_signed == "true"),
    )
    print_success(f"Contract created: {contract.contract_id}")


@cli.command("update", help="Update a contract.")
@click.option("--contract-id", prompt=True, required=True)
@click.option("--total-amount", required=False, type=float)
@click.option("--remaining-amount", required=False, type=float)
@click.option(
    "--is-signed",
    required=False,
    type=click.Choice(["true", "false"])
)
@click.pass_context
def update_contract(
        ctx,
        contract_id,
        total_amount,
        remaining_amount,
        is_signed
):
    current_employee = require_login(ctx)
    service = ContractService(ctx.obj["db_session"])
    current = service.get_contract(contract_id)

    if total_amount is None:
        total_amount = click.prompt(
            "Total amount",
            default=float(current.total_amount),
            type=float,
            show_default=True,
        )

    if remaining_amount is None:
        remaining_amount = click.prompt(
            "Remaining amount",
            default=float(current.remaining_amount),
            type=float,
            show_default=True,
        )

    if is_signed is None:
        is_signed = click.prompt(
            "Is signed",
            type=click.Choice(["true", "false"]),
            default="true" if current.is_signed else "false",
            show_default=True,
        )

    contract = service.update_contract(
        current_employee=current_employee,
        contract_id=contract_id,
        total_amount=total_amount,
        remaining_amount=remaining_amount,
        is_signed=(is_signed == "true"),
    )
    print_success(f"Contract updated: {contract.contract_id}")


def main(db_session=None, args=None):
    return run_click_app(
        cli,
        db_session=db_session,
        args=args,
        prog_name="contracts.py",
    )


if __name__ == "__main__":
    raise SystemExit(main())
