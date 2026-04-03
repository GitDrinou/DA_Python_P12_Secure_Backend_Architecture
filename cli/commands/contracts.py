import click
from cli.printers import print_collection, print_row, print_success
from cli.validators import run_click_app, require_permission, require_login
from security.permissions import (
    PERM_CONTRACTS_READ_ALL, PERM_CONTRACTS_FILTER_UNSIGNED_OR_UNPAID,
    PERM_CONTRACTS_CREATE_ALL, PERM_CONTRACTS_DELETE_ALL,
)
from services.contract_service import ContractService
from cli.interactions import prompt_if_missing, confirm_if_requested


def contract_to_dict(contract):
    return {
        "contract_id": contract.contract_id,
        "customer_name": contract.customer.full_name if contract.customer
        else None,
        "total_amount": contract.total_amount,
        "remaining_amount": contract.remaining_amount,
        "is_signed": contract.is_signed,
        "sales_name": contract.customer.sales.full_name if contract.customer
        else None,
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
@click.option("--contract-id", required=False)
@click.pass_context
def get_contract(ctx, contract_id):
    require_permission(ctx, PERM_CONTRACTS_READ_ALL)

    contract_id = prompt_if_missing(contract_id, "Contract id")

    service = ContractService(ctx.obj["db_session"])
    contract = service.get_contract(contract_id)
    print_row(contract_to_dict(contract), title="Contract")


@cli.command("create", help="Create a contract.")
@click.option("--customer-id", required=False)
@click.option("--total-amount", required=False, type=float)
@click.option("--remaining-amount", required=False, type=float)
@click.option(
    "--is-signed",
    type=click.Choice(["true", "false"]),
    required=False,
    default=None,
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

    customer_id = prompt_if_missing(customer_id, "Customer id")
    total_amount = prompt_if_missing(total_amount, "Total amount", type=float)
    remaining_amount = prompt_if_missing(
        remaining_amount,
        "Remaining amount",
        type=float,
    )

    if is_signed is None:
        is_signed = click.prompt(
            "Is signed",
            type=click.Choice(["true", "false"]),
            default="false",
            show_default=True,
        )

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
@click.option("--contract-id", required=True)
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

    contract_id = prompt_if_missing(contract_id, "Contract id")

    service = ContractService(ctx.obj["db_session"])
    current = service.get_contract(contract_id)

    total_amount = prompt_if_missing(
        total_amount,
        "Total amount",
        default=float(current.total_amount),
        type=float,
        show_default=True,
    )

    remaining_amount = prompt_if_missing(
        remaining_amount,
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


@cli.command("delete", help="Delete a contract.")
@click.option("--contract-id", required=False)
@click.option(
    "--yes",
    is_flag=True,
    help="Confirm deletion without interactive prompt.",
)
@click.pass_context
def delete_contract(ctx, contract_id, yes):
    current_employee = require_permission(ctx, PERM_CONTRACTS_DELETE_ALL)

    contract_id = prompt_if_missing(contract_id, "Contract id")
    confirm_if_requested(yes, "Do you really want to delete this contract ?")

    service = ContractService(ctx.obj["db_session"])
    service.delete_contract(
        current_employee=current_employee,
        contract_id=contract_id,
    )
    print_success("Contract deleted")


def main(db_session=None, args=None):
    return run_click_app(
        cli,
        db_session=db_session,
        args=args,
        prog_name="contracts.py",
    )


contracts_group: click.Group = cli
