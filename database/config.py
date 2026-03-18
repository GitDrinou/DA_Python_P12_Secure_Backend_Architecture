import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import declarative_base


BASE_DIR = Path(__file__).resolve().parent.parent


def load_environment(env_file: str = ".env") -> None:
    """ Load environment variables from given file"""
    env_path = BASE_DIR / env_file
    if not env_path.exists():
        raise FileNotFoundError(f"Environment file not found: {env_path}")
    load_dotenv(env_path, override=True)


def build_database_url(env_file: str = ".env"):
    """ Build SQLAlchemy database url from given file"""
    load_environment(env_file)

    db_user = os.getenv("MYSQL_USER")
    db_password = os.getenv("MYSQL_USER_PASSWORD")
    db_host = os.getenv("MYSQL_HOST", "localhost")
    db_port = int(os.getenv("MYSQL_PORT", "3306"))
    db_name = os.getenv("MYSQL_DATABASE")

    if not all([db_user, db_password, db_name]):
        raise ValueError("environment variables not set")

    return URL.create(
        drivername="mysql+pymysql",
        username=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_name,
    )


DATABASE_URL = build_database_url(".env")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

Base = declarative_base()
