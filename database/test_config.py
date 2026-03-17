from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.config import build_database_url

TEST_DATABASE_URL = build_database_url(".env.test")

test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    future=True,
)
