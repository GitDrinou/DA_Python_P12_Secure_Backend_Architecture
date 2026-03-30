from sqlalchemy import select
from core.settings import get_settings
from database.config import Base, engine
import database.models  # noqa: F401
from database.models import Employee, Role
from database.session import SessionLocal
from security.passwords import hash_password
from security.permissions import ROLE_ADMIN, ROLE_MANAGEMENT
from security.rbac import seed_rbac


def create_database():
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        seed_rbac(session)

    print("Tables created and RBAC seeded")


def check_admin(session, admin_email, admin_password):
    """
    Check if an admin user exists once
    Args:
        session: SQLAlchemy session
        admin_email(str|None): Admin email
        admin_password(str|None): Admin password
    """
    if not admin_email:
        raise ValueError("Admin email is not configured.")

    if not admin_password:
        raise ValueError("Admin password is not configured.")

    role = session.execute(
        select(Role).where(Role.name == ROLE_ADMIN)
    ).scalar_one_or_none()

    if role is None:
        raise ValueError(f"Role '{ROLE_MANAGEMENT}' not found.")

    existing_admin = session.execute(
        select(Employee).where(Employee.email == admin_email)
    ).scalar_one_or_none()

    if existing_admin is not None:
        updated = False
        if existing_admin.role_id != role.role_id:
            existing_admin.role_id = role.role_id
            updated = True
        if not existing_admin.is_active:
            existing_admin.is_active = True
            updated = True
        if updated:
            session.commit()
            session.refresh(existing_admin)

        return existing_admin, False

    admin = Employee(
        full_name="Admin EPIC EVENTS",
        email=admin_email,
        password_hash=hash_password(admin_password),
        is_active=True,
        role_id=role.role_id,
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)

    return admin, True


def create_admin():
    settings = get_settings()

    with SessionLocal() as session:
        admin, created = check_admin(
            session=session,
            admin_email=settings.admin.email,
            admin_password=settings.admin.password,
        )
        if created:
            print("Created admin user")
        else:
            print("Admin user already exists or was updated")

        return admin


if __name__ == "__main__":
    create_database()
    create_admin()
