from sqlalchemy import select
from core.settings import get_settings
from database.config import Base, engine
import database.models  # noqa: F401
from database.models import Employee, Role
from database.session import SessionLocal
from security.passwords import hash_password
from security.rbac import seed_rbac


def create_database():
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        seed_rbac(session)

    print("Tables created and RBAC seeded")


def create_admin():
    settings = get_settings()

    with SessionLocal() as session:
        role = session.execute(
            select(Role).where(Role.name == "gestion")
        ).scalar_one_or_none()

        if not role:
            raise ValueError("Role 'gestion' not found.")

        admin = Employee(
            full_name="Admin EPIC EVENTS",
            email=settings.admin.email,
            password_hash=hash_password(settings.admin.password),
            is_active=True,
            role_id=role.role_id,
        )

        session.add(admin)
        session.commit()

        print("Created admin user")


if __name__ == "__main__":
    create_database()
    create_admin()
