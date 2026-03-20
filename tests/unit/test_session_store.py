from security import session_store


def test_save_and_load_session_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "sessions.json"
    )

    session_store.save_session("access-token", "refresh-token")
    saved = session_store.load_session()

    assert saved == {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
    }
    assert session_store.SESSION_FILE.exists()


def test_clear_session_deletes_existing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(
        session_store,
        "SESSION_FILE",
        tmp_path / "sessions.json"
    )
    session_store.save_session("access-token", "refresh-token")

    session_store.clear_session()

    assert session_store.load_session() is None
    assert not session_store.SESSION_FILE.exists()
