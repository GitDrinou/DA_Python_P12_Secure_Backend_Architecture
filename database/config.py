from sqlalchemy import create_engine, URL
from sqlalchemy.orm import declarative_base
from core.settings import get_settings


def build_database_url(env_file=".env"):
    """ Build SQLAlchemy database url from given file"""
    settings = get_settings(env_file).database

    return URL.create(
        drivername="mysql+pymysql",
        username=settings.user,
        password=settings.password,
        host=settings.host,
        port=settings.port,
        database=settings.name,
    )


DATABASE_URL = build_database_url(".env")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

Base = declarative_base()
