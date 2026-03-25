from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
from database.models import Event, Contract, Employee
from security import (
    can_create_event,
    can_update_event,
    has_permission,
)
from security.permissions import (
    PERM_EVENTS_ASSIGN_SUPPORT,
    ROLE_SUPPORT,
)


class EventService:
    def __init__(self, db_session):
        self.db_session = db_session

    def list_events(self, without_support=False, assigned_to_employee_id=None):
        """
        List events.
        Args:
            without_support (boolean): filter events without support assigned
            assigned_to_employee_id (str): filter events assigned to support
        """
        query = (
            self.db_session.query(Event)
            .options(
                joinedload(Event.contract).joinedload(Contract.customer),
                joinedload(Event.support),
            )
            .order_by(Event.start_date.asc())
        )

        if without_support:
            query = query.filter(Event.support_id.is_(None))

        if assigned_to_employee_id is not None:
            query = query.filter(Event.support_id == assigned_to_employee_id)

        return query.all()

    def get_event(self, event_id):
        """
        Get event by id.
        """
        event = (
            self.db_session.query(Event)
            .options(
                joinedload(Event.contract).joinedload(Contract.customer),
                joinedload(Event.support),
            )
            .filter(Event.event_id == event_id)
            .first()
        )

        if event is None:
            raise ValueError("Event not found")

        return event

    def create_event(
        self,
        current_employee,
        contract_id,
        title,
        start_date,
        end_date,
        location,
        attendees,
        notes=None,
    ):
        """
        Create a new event for a signed contract owned by the current sales.
        Args:
            current_employee (object): current employee
            contract_id (str): contract id
            title (str): event title
            start_date (datetime): event start date
            end_date (datetime): event end date
            location (str): event location
            attendees (int): event attendees
            notes (str): event notes
        """
        contract = (
            self.db_session.query(Contract)
            .options(joinedload(Contract.customer))
            .filter(Contract.contract_id == contract_id)
            .first()
        )

        if contract is None:
            raise ValueError("Contract not found")

        if not can_create_event(current_employee, contract):
            raise ValueError("You are not allowed to create this event")

        start_date = self._format_datetime(start_date)
        end_date = self._format_datetime(end_date)
        attendees = int(attendees)

        self._validate_event_dates_and_attendees(
            start_date=start_date,
            end_date=end_date,
            attendees=attendees,
        )

        event = Event(
            contract_id=contract.contract_id,
            title=title,
            start_date=start_date,
            end_date=end_date,
            location=location,
            attendees=attendees,
            notes=notes,
        )

        self.db_session.add(event)
        self.db_session.commit()
        self.db_session.refresh(event)

        return event

    def update_event(
        self,
        event_id,
        current_employee,
        title=None,
        start_date=None,
        end_date=None,
        location=None,
        attendees=None,
        notes=None,
    ):
        """
        Update an event.
        - manager can update any event
        - support can update only events assigned to them
        Args:
            event_id (str): event id
            current_employee (object): current employee
            title (str): event title
            start_date (str|datetime): event start date
            end_date (str|datetime): event end date
            location (str): event location
            attendees (int): event attendees
            notes (str): event notes
        """
        event = self.get_event(event_id)

        if not can_update_event(current_employee, event):
            raise ValueError("You are not allowed to update this event")

        new_start_date = (
            self._format_datetime(start_date)
            if start_date is not None
            else event.start_date
        )
        new_end_date = (
            self._format_datetime(end_date)
            if end_date is not None
            else event.end_date
        )
        new_attendees = (
            int(attendees)
            if attendees is not None
            else event.attendees
        )

        self._validate_event_dates_and_attendees(
            start_date=new_start_date,
            end_date=new_end_date,
            attendees=new_attendees,
        )

        if title is not None:
            event.title = title
        if start_date is not None:
            event.start_date = new_start_date
        if end_date is not None:
            event.end_date = new_end_date
        if location is not None:
            event.location = location
        if attendees is not None:
            event.attendees = new_attendees
        if notes is not None:
            event.notes = notes

        self.db_session.commit()
        self.db_session.refresh(event)

        return event

    def assign_support(self, event_id, current_employee, support_id):
        """
        Assign a support employee to an event.
        Args:
            event_id (str): event id
            current_employee (object): current employee
            support_id (str): support employee id
        """
        event = self.get_event(event_id)

        if not has_permission(current_employee, PERM_EVENTS_ASSIGN_SUPPORT):
            raise ValueError("You are not allowed to assign support to events")

        support_employee = (
            self.db_session.query(Employee)
            .options(joinedload(Employee.role))
            .filter(Employee.employee_id == support_id)
            .first()
        )

        if support_employee is None:
            raise ValueError("Support employee not found")

        if (
                support_employee.role is None
                or support_employee.role.name != ROLE_SUPPORT
        ):
            raise ValueError("Selected employee is not a support employee")

        event.support_id = support_employee.employee_id

        self.db_session.commit()
        self.db_session.refresh(event)

        return event

    @staticmethod
    def _format_datetime(value):
        if isinstance(value, datetime):
            dt = value
        else:
            text = str(value).strip()
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            dt = datetime.fromisoformat(text)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt

    @staticmethod
    def _validate_event_dates_and_attendees(start_date, end_date, attendees):
        if end_date <= start_date:
            raise ValueError("End date must be after start date")

        if attendees < 0:
            raise ValueError("Attendees cannot be negative")
