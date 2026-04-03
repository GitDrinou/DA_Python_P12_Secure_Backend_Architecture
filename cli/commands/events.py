from datetime import datetime, timezone
import click
from cli.printers import print_collection, print_row, print_success
from cli.validators import run_click_app, require_permission, require_login
from security.permissions import (
    PERM_EVENTS_READ_ALL, PERM_EVENTS_FILTER_WITHOUT_SUPPORT,
    PERM_EVENTS_FILTER_ASSIGNED_TO_ME,
    PERM_EVENTS_CREATE_FOR_SIGNED_CONTRACT_OWNED_CUSTOMERS,
    PERM_EVENTS_ASSIGN_SUPPORT, PERM_EVENTS_DELETE_OWNED_CUSTOMERS
)
from services.event_service import EventService
from cli.interactions import prompt_if_missing, confirm_if_requested


def parse_datetime(value):
    text = str(value).strip()
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
    except ValueError:
        dt = datetime.strptime(text, "%d/%m/%Y")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def event_to_dict(event):
    return {
        "event_id": event.event_id,
        "title": event.title,
        "start_date": event.start_date,
        "end_date": event.end_date,
        "location": event.location,
        "attendees": event.attendees,
        "contract_id": event.contract_id,
        "customer_name": (
            event.contract.customer.full_name
            if event.contract and event.contract.customer
            else None
        ),
        "support_name": event.support.full_name if event.support else None,
        "notes": event.notes,
    }


@click.group(help="Manage events.")
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.command("list", help="List all events.")
@click.option("--without-support", is_flag=True, default=False)
@click.option("--assigned-to-me", is_flag=True, default=False)
@click.pass_context
def list_events(ctx, without_support, assigned_to_me):
    current_employee = require_permission(ctx, PERM_EVENTS_READ_ALL)
    service = EventService(ctx.obj["db_session"])

    if without_support and assigned_to_me:
        raise click.ClickException(
            "Choose only one filter between --without-support and "
            "--assigned-to-me"
        )

    if without_support:
        require_permission(ctx, PERM_EVENTS_FILTER_WITHOUT_SUPPORT)
        events = service.list_events_without_support(current_employee)
        print_collection(
            [event_to_dict(event) for event in events],
            title="Events without support",
        )
        return

    if assigned_to_me:
        require_permission(ctx, PERM_EVENTS_FILTER_ASSIGNED_TO_ME)
        events = service.list_my_events(current_employee)
        print_collection(
            [event_to_dict(event) for event in events],
            title="My events",
        )
        return

    events = service.list_events()
    print_collection(
        [event_to_dict(event) for event in events],
        title="Events",
    )


@cli.command("get", help="Display an event.")
@click.option("--event-id", required=True)
@click.pass_context
def get_event(ctx, event_id):
    require_permission(ctx, PERM_EVENTS_READ_ALL)

    event_id = prompt_if_missing(event_id, "Event id")

    service = EventService(ctx.obj["db_session"])
    event = service.get_event(event_id)
    print_row(event_to_dict(event), title="Event")


@cli.command("create", help="Create an event.")
@click.option("--contract-id", required=False)
@click.option("--title", required=False)
@click.option("--start-date", required=False)
@click.option("--end-date", required=False)
@click.option("--location", required=False)
@click.option("--attendees", required=False, type=int)
@click.option("--notes", required=False)
@click.pass_context
def create_event(
        ctx,
        contract_id,
        title,
        start_date,
        end_date,
        location,
        attendees,
        notes
):
    current_employee = require_permission(
        ctx,
        PERM_EVENTS_CREATE_FOR_SIGNED_CONTRACT_OWNED_CUSTOMERS,
    )

    contract_id = prompt_if_missing(contract_id, "Contract id")
    title = prompt_if_missing(title, "Title")
    start_date = prompt_if_missing(start_date, "Start date")
    end_date = prompt_if_missing(end_date, "End date")
    location = prompt_if_missing(location, "Location")
    attendees = prompt_if_missing(attendees, "Attendees", type=int)

    service = EventService(ctx.obj["db_session"])
    event = service.create_event(
        current_employee=current_employee,
        contract_id=contract_id,
        title=title,
        start_date=parse_datetime(start_date),
        end_date=parse_datetime(end_date),
        location=location,
        attendees=attendees,
        notes=notes,
    )
    print_success(f"Event created: {event.event_id}")


@cli.command("update", help="Update an event.")
@click.option("--event-id", required=False)
@click.option("--title", required=False)
@click.option("--start-date", required=False)
@click.option("--end-date", required=False)
@click.option("--location", required=False)
@click.option("--attendees", required=False, type=int)
@click.option("--notes", required=False)
@click.pass_context
def update_event(
        ctx,
        event_id,
        title,
        start_date,
        end_date,
        location,
        attendees,
        notes
):
    current_employee = require_login(ctx)

    event_id = prompt_if_missing(event_id, "Event id")

    service = EventService(ctx.obj["db_session"])
    current = service.get_event(event_id)

    title = prompt_if_missing(
        title,
        "Title",
        default=current.title,
        show_default=True,
    )

    start_date = prompt_if_missing(
        start_date,
        "Start date",
        default=current.start_date.isoformat(),
        show_default=True,
    )

    end_date = prompt_if_missing(
        end_date,
        "End date",
        default=current.end_date.isoformat(),
        show_default=True,
    )

    location = prompt_if_missing(
        location,
        "Location",
        default=current.location,
        show_default=True,
    )

    attendees = prompt_if_missing(
        attendees,
        "Attendees",
        default=current.attendees,
        type=int,
        show_default=True,
    )

    if notes is None:
        notes = click.prompt(
            "Notes",
            default=current.notes or "",
            show_default=False,
        )

    event = service.update_event(
        event_id=event_id,
        current_employee=current_employee,
        title=title,
        start_date=parse_datetime(start_date),
        end_date=parse_datetime(end_date),
        location=location,
        attendees=attendees,
        notes=notes,
    )
    print_success(f"Event updated: {event.event_id}")


@cli.command("assign-support", help="Assign a support employee to an event.")
@click.option("--event-id", required=False)
@click.option("--support-id", prompt=True, required=False)
@click.pass_context
def assign_support(ctx, event_id, support_id):
    current_employee = require_permission(ctx, PERM_EVENTS_ASSIGN_SUPPORT)

    event_id = prompt_if_missing(event_id, "Event id")
    support_id = prompt_if_missing(support_id, "Support id")

    service = EventService(ctx.obj["db_session"])
    event = service.assign_support(
        event_id=event_id,
        current_employee=current_employee,
        support_id=support_id,
    )
    print_success(f"Support assigned to event: {event.event_id}")


@cli.command("delete", help="Delete an event.")
@click.option("--event-id", prompt=True, required=False)
@click.option(
    "--yes",
    is_flag=True,
    help="Confirm deletion without interactive prompt.",
)
@click.pass_context
def delete_event(ctx, event_id, yes):
    current_employee = require_permission(
        ctx,
        PERM_EVENTS_DELETE_OWNED_CUSTOMERS
    )

    event_id = prompt_if_missing(event_id, "Event id")
    confirm_if_requested(yes, "Do you really want to delete this event ?")

    service = EventService(ctx.obj["db_session"])
    service.delete_event(
        current_employee=current_employee,
        event_id=event_id
    )
    print_success("Event deleted")


def main(db_session=None, args=None):
    return run_click_app(
        cli,
        db_session=db_session,
        args=args,
        prog_name="events.py",
    )


events_group: click.Group = cli
