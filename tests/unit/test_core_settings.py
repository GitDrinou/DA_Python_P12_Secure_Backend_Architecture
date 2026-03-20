from pathlib import Path
import pytest
from core.settings import clear_settings_cache, get_settings, load_environment


@pytest.fixture(autouse=True)
def clear_cache_between_tests():
    clear_settings_cache()
    yield
    clear_settings_cache()


def test_load_environment_reads_given_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env.custom"
    env_file.write_text(
        "\n".join([
            "MYSQL_USER=test_user",
            "MYSQL_USER_PASSWORD=test_password",
            "MYSQL_DATABASE=test_db",
        ]),
        encoding="utf-8",
    )

    load_environment(str(env_file))

    assert Path(env_file).exists()


def test_get_settings_builds_typed_settings_from_env_file(tmp_path):
    env_file = tmp_path / ".env.custom"
    session_dir = tmp_path / "sessions"
    env_file.write_text(
        "\n".join([
            "MYSQL_USER=test_user",
            "MYSQL_USER_PASSWORD=test_password",
            "MYSQL_HOST=db.example.local",
            "MYSQL_PORT=3307",
            "MYSQL_DATABASE=test_db",
            "JWT_SECRET_KEY=super-secret",
            "JWT_ALGORITHM=HS512",
            "JWT_ISSUER=crm-tests",
            "ACCESS_TOKEN_EXPIRE_MINUTES=30",
            "REFRESH_TOKEN_EXPIRE_DAYS=14",
            "CRM_ADMIN_USER_EMAIL=admin@example.com",
            "CRM_ADMIN_USER_PASSWORD=change-me",
            f"EPIC_EVENTS_CRM_SESSION_DIR={session_dir}",
        ]),
        encoding="utf-8",
    )

    settings = get_settings(str(env_file))

    assert settings.database.user == "test_user"
    assert settings.database.password == "test_password"
    assert settings.database.host == "db.example.local"
    assert settings.database.port == 3307
    assert settings.database.name == "test_db"
    assert settings.jwt.secret_key == "super-secret"
    assert settings.jwt.algorithm == "HS512"
    assert settings.jwt.issuer == "crm-tests"
    assert settings.jwt.access_token_expire_minutes == 15
    assert settings.jwt.refresh_token_expire_days == 7
    assert settings.admin.email == "admin@example.com"
    assert settings.admin.password == "change-me"
    assert settings.session.directory == session_dir
