import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import select
from database.config import Base, engine
import database.models  # noqa: F401
from database.models import Employee, Role
from database.session import SessionLocal
from security.passwords import hash_password
from security.rbac import seed_rbac

BASE_DIR = Path(__file__).resolve().parent.parent


def load_environment(env_file="P12/.env"):
    """ Load environment variables from given file"""
    env_path = BASE_DIR / env_file
    if not env_path.exists():
        raise FileNotFoundError(f"Environment file not found: {env_path}")
    load_dotenv(env_path, override=True)


def create_database():
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        seed_rbac(session)

    print("Tables created and RBAC seeded")


def create_admin():
    load_environment()

    with SessionLocal() as session:
        role = session.execute(
            select(Role).where(Role.name == "gestion")
        ).scalar_one_or_none()

        if not role:
            raise ValueError("Role 'gestion' not found.")

        admin = Employee(
            full_name="Admin EPIC EVENTS",
            email=os.getenv("CRM_ADMIN_USER_EMAIL"),
            password_hash=hash_password(os.getenv("CRM_ADMIN_USER_PASSWORD")),
            is_active=True,
            role_id=role.role_id,
        )

        session.add(admin)
        session.commit()

        print("Created admin user")


if __name__ == "__main__":
    create_database()
    create_admin()
