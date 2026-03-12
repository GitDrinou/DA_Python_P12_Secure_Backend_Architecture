from database.config import Base, engine
import database.models  # noqa: F401


def create_database():
    Base.metadata.create_all(engine)
    print("Tables created")


if __name__ == "__main__":
    create_database()
