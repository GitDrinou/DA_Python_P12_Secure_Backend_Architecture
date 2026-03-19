from cli.app import render_menu, run_main_menu
from security.rbac import seed_rbac
from database.models import Role, Employee
from security.passwords import hash_password


def _create_employee(db_session, role_name, email):
    role = db_session.query(Role).filter(Role.name == role_name).first()
    employee = Employee(
        full_name="Test User",
        email=email,
        password_hash=hash_password("Password123!"),
        is_active=True,
        role_id=role.role_id,
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee


def test_render_menu_displays_role_specific_entries(db_session):
    seed_rbac(db_session)
    employee = _create_employee(db_session, "support", "support2@mail.com")

    output = render_menu(employee)

    assert "Connecté : Test User (support)" in output
    assert "Lister les événements" in output
    assert "Créer un client" not in output


def test_run_main_menu_logs_out(monkeypatch, db_session, tmp_path):
    from security import session_store

    monkeypatch.setattr(session_store, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(session_store, "SESSION_FILE", tmp_path / "session.json")

    seed_rbac(db_session)
    employee = _create_employee(db_session, "support", "support3@mail.com")

    printed = []

    def fake_print(message):
        printed.append(message)

    inputs = iter(["0"])

    def fake_input(_prompt):
        return next(inputs)

    run_main_menu(employee, input_func=fake_input, print_func=fake_print)

    assert any("Déconnexion réussie." in line for line in printed)