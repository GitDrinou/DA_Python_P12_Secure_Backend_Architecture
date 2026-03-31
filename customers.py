import click
from cli.printers import print_collection, print_row, print_success
from cli.verificators import run_click_app, require_permission
from security.permissions import (
    PERM_CUSTOMERS_READ_ALL, PERM_CUSTOMERS_CREATE_OWNED,
    PERM_CUSTOMERS_UPDATE_OWNED, PERM_CUSTOMERS_DELETE_OWNED,
)
from services.customer_service import CustomerService


def customer_to_dict(customer):
    return {
        "customer_id": customer.customer_id,
        "full_name": customer.full_name,
        "email": customer.email,
        "phone": customer.phone,
        "company_name": customer.company_name,
        "sales_name": customer.sales.full_name,
    }


@click.group(help="Manage customers.")
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.command("list", help="List all customers.")
@click.pass_context
def list_customers(ctx):
    require_permission(ctx, PERM_CUSTOMERS_READ_ALL)
    service = CustomerService(ctx.obj["db_session"])
    customers = service.list_customers()
    print_collection(
        [customer_to_dict(customer) for customer in customers],
        title="Customers",
    )


@cli.command("get", help="Display a customer.")
@click.option("--customer-id", prompt=True, required=True)
@click.pass_context
def get_customer(ctx, customer_id):
    require_permission(ctx, PERM_CUSTOMERS_READ_ALL)
    service = CustomerService(ctx.obj["db_session"])
    customer = service.get_customer(customer_id)
    print_row(customer_to_dict(customer), title="Customer")


@cli.command("create", help="Create a customer.")
@click.option("--full-name", prompt=True, required=True)
@click.option("--email", prompt=True, required=True)
@click.option("--phone", prompt=True, required=True)
@click.option("--company-name", prompt=True, required=True)
@click.pass_context
def create_customer(ctx, full_name, email, phone, company_name):
    current_employee = require_permission(ctx, PERM_CUSTOMERS_CREATE_OWNED)
    service = CustomerService(ctx.obj["db_session"])
    customer = service.create_customer(
        current_employee=current_employee,
        full_name=full_name,
        email=email,
        phone=phone,
        company_name=company_name,
    )
    print_success(
        f"Customer created: {customer.full_name} ({customer.customer_id})"
    )


@cli.command("update", help="Update a customer.")
@click.option("--customer-id", prompt=True, required=True)
@click.option("--full-name", required=False)
@click.option("--email", required=False)
@click.option("--phone", required=False)
@click.option("--company-name", required=False)
@click.pass_context
def update_customer(ctx, customer_id, full_name, email, phone, company_name):
    current_employee = require_permission(ctx, PERM_CUSTOMERS_UPDATE_OWNED)
    service = CustomerService(ctx.obj["db_session"])
    current = service.get_customer(customer_id)

    if full_name is None:
        full_name = click.prompt(
            "Full name",
            default=current.full_name,
            show_default=True,
        )
    if email is None:
        email = click.prompt(
            "Email",
            default=current.email,
            show_default=True,
        )
    if phone is None:
        phone = click.prompt(
            "Phone",
            default=current.phone,
            show_default=True,
        )
    if company_name is None:
        company_name = click.prompt(
            "Company name",
            default=current.company_name,
            show_default=True,
        )

    customer = service.update_customer(
        current_employee=current_employee,
        customer_id=customer_id,
        full_name=full_name,
        email=email,
        phone=phone,
        company_name=company_name,
    )
    print_success(
        f"Customer updated: {customer.full_name} ({customer.customer_id})"
    )


@cli.command("delete", help="Delete a customer.")
@click.option("--customer-id", prompt=True, required=True)
@click.confirmation_option(
    prompt="Do you really want to delete this customer ?"
)
@click.pass_context
def delete_customer(ctx, customer_id):
    current_employee = require_permission(ctx, PERM_CUSTOMERS_DELETE_OWNED)
    service = CustomerService(ctx.obj["db_session"])
    service.delete_customer(
        current_employee=current_employee,
        customer_id=customer_id
    )
    print_success("Customer deleted")


def main(db_session=None, args=None):
    return run_click_app(
        cli,
        db_session=db_session,
        args=args,
        prog_name="customers.py",
    )


if __name__ == "__main__":
    raise SystemExit(main())
