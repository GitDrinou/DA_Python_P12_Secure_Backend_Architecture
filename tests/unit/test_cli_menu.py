from cli.menu import build_menu_for_employee
from database.models import Role, Employee
from security import seed_rbac
from security.passwords import hash_password
from security.permissions import ROLE_SALES, ROLE_MANAGEMENT


def _create_employee(db_session, role_name, email):
    role = db_session.query(Role).filter(Role.name == role_name).first()
    employee = Employee(
        full_name=f"{role_name.title()} Employee",
        email=email,
        password_hash=hash_password("Password123!"),
        is_active=True,
        role_id=role.role_id
    )

    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    return employee


def test_build_menu_for_commercial(db_session):
    seed_rbac(db_session)
    employee = _create_employee(db_session, ROLE_SALES, "sales@example.com")

    menu = build_menu_for_employee(employee)
    labels = {item["label"] for item in menu}

    assert "Lister les clients" in labels
    assert "Créer un client" in labels
    assert "Créer un événement" in labels
    assert "Assigner un support à un événement" not in labels
    assert "Gérer les collaborateurs" not in labels


def test_build_menu_for_management(db_session):
    seed_rbac(db_session)
    employee = _create_employee(
        db_session,
        ROLE_MANAGEMENT,
        "gestion@mail.com"
    )

    menu = build_menu_for_employee(employee)
    labels = {item["label"] for item in menu}

    assert "Gérer les collaborateurs" in labels
    assert "Assigner un support à un événement" in labels
    assert "Créer un contrat" in labels
    assert "Créer un client" not in labels
