import argparse
from datetime import datetime, timezone
from cli.printers import print_collection, print_row, print_success
from cli.verificators import (
    permission_required,
    login_required,
    handle_cli_errors,
)
from database.session import SessionLocal
from security import has_permission, AuthorizationError
from security.permissions import (
    PERM_EVENTS_READ_ALL,
    PERM_EVENTS_FILTER_WITHOUT_SUPPORT,
    PERM_EVENTS_FILTER_ASSIGNED_TO_ME,
    PERM_EVENTS_CREATE_FOR_SIGNED_CONTRACT_OWNED_CUSTOMERS,
    PERM_EVENTS_ASSIGN_SUPPORT,
)
from services.event_service import EventService


def build_parser():
    parser = argparse.ArgumentParser(prog="events.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List events")
    list_parser.add_argument(
        "--without-support",
        action="store_true",
        help="Filter events without support assigned",
    )
    list_parser.add_argument(
        "--assigned-to-me",
        action="store_true",
        help="Filter events assigned to current support user",
    )

    get_parser = subparsers.add_parser("get", help="Get event details")
    get_parser.add_argument("--event-id", required=True)

    create_parser = subparsers.add_parser("create", help="Create a new event")
    create_parser.add_argument("--contract-id", required=True)
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--start-date", required=True)
    create_parser.add_argument("--end-date", required=True)
    create_parser.add_argument("--location", required=True)
    create_parser.add_argument("--attendees", required=True)
    create_parser.add_argument("--notes")

    update_parser = subparsers.add_parser("update", help="Update an event")
    update_parser.add_argument("--event-id", required=True)
    update_parser.add_argument("--title")
    update_parser.add_argument("--start-date")
    update_parser.add_argument("--end-date")
    update_parser.add_argument("--location")
    update_parser.add_argument("--attendees")
    update_parser.add_argument("--notes")

    assign_parser = subparsers.add_parser(
        "assign-support",
        help="Assign a support contact to an event",
    )
    assign_parser.add_argument("--event-id", required=True)
    assign_parser.add_argument("--support-id", required=True)

    return parser


def parse_datetime(value):
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
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
        "notes": event.notes,
        "contract_id": event.contract_id,
        "customer_name": (
            event.contract.customer.full_name
            if event.contract and event.contract.customer
            else None
        ),
        "support_id": event.support_id,
        "support_name": event.support.full_name if event.support else None,
    }


@permission_required(PERM_EVENTS_READ_ALL)
def handle_list(args, current_employee=None, db_session=None):
    if args.without_support and args.assigned_to_me:
        raise ValueError(
            "Choose only one filter between --without-support and "
            "--assigned-to-me"
        )

    if args.without_support and not has_permission(
        current_employee,
        PERM_EVENTS_FILTER_WITHOUT_SUPPORT,
    ):
        raise AuthorizationError(
            f"You don't have permission: {PERM_EVENTS_FILTER_WITHOUT_SUPPORT}"
        )

    if args.assigned_to_me and not has_permission(
        current_employee,
        PERM_EVENTS_FILTER_ASSIGNED_TO_ME,
    ):
        raise AuthorizationError(
            f"You don't have permission: {PERM_EVENTS_FILTER_ASSIGNED_TO_ME}"
        )

    service = EventService(db_session)
    assigned_to_employee_id = (
        current_employee.employee_id if args.assigned_to_me else None
    )
    events = service.list_events(
        without_support=args.without_support,
        assigned_to_employee_id=assigned_to_employee_id,
    )
    print_collection([event_to_dict(event) for event in events])
    return 0


@permission_required(PERM_EVENTS_READ_ALL)
def handle_get(event_id, current_employee=None, db_session=None):
    service = EventService(db_session)
    event = service.get_event(event_id)
    print_row(event_to_dict(event))
    return 0


@permission_required(PERM_EVENTS_CREATE_FOR_SIGNED_CONTRACT_OWNED_CUSTOMERS)
def handle_create(args, current_employee=None, db_session=None):
    service = EventService(db_session)

    event = service.create_event(
        current_employee=current_employee,
        contract_id=args.contract_id,
        title=args.title,
        start_date=parse_datetime(args.start_date),
        end_date=parse_datetime(args.end_date),
        location=args.location,
        attendees=args.attendees,
        notes=args.notes,
    )

    print_success(f"Event created: {event.event_id}")
    return 0


@login_required
def handle_update(args, current_employee=None, db_session=None):
    service = EventService(db_session)

    event = service.update_event(
        event_id=args.event_id,
        current_employee=current_employee,
        title=args.title,
        start_date=parse_datetime(args.start_date) if args.start_date else
        None,
        end_date=parse_datetime(args.end_date) if args.end_date else None,
        location=args.location,
        attendees=args.attendees,
        notes=args.notes,
    )

    print_success(f"Event updated: {event.event_id}")
    return 0


@permission_required(PERM_EVENTS_ASSIGN_SUPPORT)
def handle_assign_support(args, current_employee=None, db_session=None):
    service = EventService(db_session)

    event = service.assign_support(
        event_id=args.event_id,
        current_employee=current_employee,
        support_id=args.support_id,
    )

    print_success(f"Support assigned to event: {event.event_id}")
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
            return handle_get(args.event_id, db_session=db_session)

        if args.command == "create":
            return handle_create(args, db_session=db_session)

        if args.command == "update":
            return handle_update(args, db_session=db_session)

        if args.command == "assign-support":
            return handle_assign_support(args, db_session=db_session)

        return 1
    finally:
        if created_session:
            db_session.close()


if __name__ == "__main__":
    raise SystemExit(main())
