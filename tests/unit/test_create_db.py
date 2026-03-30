from sqlalchemy import select
from create_db import check_admin
from database.models import Employee
from security.permissions import ROLE_ADMIN
from security.rbac import seed_rbac
from database.models import Role


def test_check_admin_creates_admin_when_missing(db_session):
    seed_rbac(db_session)

    admin, created = check_admin(
        session=db_session,
        admin_email="admin@test.com",
        admin_password="AdminPassword123!",
    )

    assert created is True
    assert admin.email == "admin@test.com"
    assert admin.full_name == "Admin EPIC EVENTS"
    assert admin.is_active is True
    assert admin.role.name == ROLE_ADMIN

    persisted = db_session.execute(
        select(Employee).where(Employee.email == "admin@test.com")
    ).scalar_one()

    assert persisted.employee_id == admin.employee_id


def test_check_admin_does_not_duplicate_existing_admin(db_session):
    seed_rbac(db_session)

    first_admin, first_created = check_admin(
        session=db_session,
        admin_email="admin@test.com",
        admin_password="AdminPassword123!",
    )

    second_admin, second_created = check_admin(
        session=db_session,
        admin_email="admin@test.com",
        admin_password="AdminPassword123!",
    )

    assert first_created is True
    assert second_created is False
    assert first_admin.employee_id == second_admin.employee_id

    admins = db_session.execute(
        select(Employee).where(Employee.email == "admin@test.com")
    ).scalars().all()

    assert len(admins) == 1


def test_check_admin_raises_if_management_role_is_missing(db_session):
    try:
        check_admin(
            session=db_session,
            admin_email="admin@test.com",
            admin_password="AdminPassword123!",
        )
        assert False, "Expected ValueError to be raised"
    except ValueError as exc:
        assert str(exc) == "Role 'gestion' not found."


def test_check_admin_raises_if_admin_email_is_missing(db_session):
    seed_rbac(db_session)

    try:
        check_admin(
            session=db_session,
            admin_email=None,
            admin_password="AdminPassword123!",
        )
        assert False, "Expected ValueError to be raised"
    except ValueError as exc:
        assert str(exc) == "Admin email is not configured."


def test_check_admin_raises_if_admin_password_is_missing(db_session):
    seed_rbac(db_session)

    try:
        check_admin(
            session=db_session,
            admin_email="admin@example.com",
            admin_password=None,
        )
        assert False, "Expected ValueError to be raised"
    except ValueError as exc:
        assert str(exc) == "Admin password is not configured."


def test_check_admin_reactivates_existing_admin_and_moves_it_to_admin_role(
    db_session,
):
    seed_rbac(db_session)

    admin_role = db_session.execute(
        select(Role).where(Role.name == ROLE_ADMIN)
    ).scalar_one()

    admin, _ = check_admin(
        session=db_session,
        admin_email="admin@test.com",
        admin_password="AdminPassword123!",
    )

    admin.is_active = False
    db_session.commit()

    updated_admin, created = check_admin(
        session=db_session,
        admin_email="admin@test.com",
        admin_password="AdminPassword123!",
    )

    assert created is False
    assert updated_admin.is_active is True
    assert updated_admin.role_id == admin_role.role_id
