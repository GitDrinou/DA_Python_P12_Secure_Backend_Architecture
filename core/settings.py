import os
from functools import lru_cache
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SESSION_DIR = Path.home() / ".epic_events_crm"
DEFAULT_SESSION_FILE_NAME = "session.json"


@dataclass(frozen=True)
class DatabaseSettings:
    user: str
    password: str
    host: str
    port: int
    name: str


@dataclass(frozen=True)
class JwtSettings:
    secret_key: str
    algorithm: str
    issuer: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int


@dataclass(frozen=True)
class AdminSettings:
    email: str | None
    password: str | None


@dataclass(frozen=True)
class SessionSettings:
    directory: Path
    file_path: Path


@dataclass(frozen=True)
class Settings:
    database: DatabaseSettings
    jwt: JwtSettings
    admin: AdminSettings
    session: SessionSettings


def _resolve_env_path(env_file=".env"):
    env_path = Path(env_file)
    if not env_path.is_absolute():
        env_path = BASE_DIR / env_file
    return env_path


def load_environment(env_file=".env"):
    env_path = _resolve_env_path(env_file)
    if not env_path.exists():
        raise FileNotFoundError(f"Environment file not found: {env_file}")
    load_dotenv(env_path, override=True)
    return env_path


@lru_cache(maxsize=None)
def get_settings(env_file=".env"):
    load_environment(env_file)

    db_user = os.getenv("MYSQL_USER")
    db_password = os.getenv("MYSQL_USER_PASSWORD")
    db_host = os.getenv("MYSQL_HOST", "localhost")
    db_port = int(os.getenv("MYSQL_PORT", "3306"))
    db_name = os.getenv("MYSQL_DATABASE")

    if not all([db_user, db_password, db_name, db_host]):
        raise ValueError("Environment variables not set")

    session_directory = Path(
        os.getenv("EPIC_EVENTS_CRM_SESSION_DIR", str(DEFAULT_SESSION_DIR))
    ).expanduser()

    return Settings(
        database=DatabaseSettings(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            name=db_name,
        ),
        jwt=JwtSettings(
            secret_key=os.getenv("JWT_SECRET_KEY", ""),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            issuer=os.getenv("JWT_ISSUER", "epic-events-crm"),
            access_token_expire_minutes=int(
                os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15")
            ),
            refresh_token_expire_days=int(
                os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
            ),
        ),
        admin=AdminSettings(
            email=os.getenv("CRM_ADMIN_USER_EMAIL"),
            password=os.getenv("CRM_ADMIN_USER_PASSWORD"),
        ),
        session=SessionSettings(
            directory=session_directory,
            file_path=session_directory / DEFAULT_SESSION_FILE_NAME,
        ),
    )


def clear_settings_cache():
    get_settings.cache_clear()
