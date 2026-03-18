import json
import os
from pathlib import Path

SESSION_DIR = Path.home() / ".epic_events_crm"
SESSION_FILE = SESSION_DIR / "sessions.json"


def save_session(access_token, refresh_token):
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

    os.chmod(SESSION_FILE, 0o600)


def load_session():
    if not SESSION_FILE.exists():
        return None

    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def clear_session():
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
