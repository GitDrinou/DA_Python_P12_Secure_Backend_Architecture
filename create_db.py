from database.config import Base, engine
import database.models  # noqa: F401
from database.session import SessionLocal
from security.rbac import seed_rbac


def create_database():
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        seed_rbac(session)

    print("Tables created and RBAC seeded")


if __name__ == "__main__":
    create_database()
