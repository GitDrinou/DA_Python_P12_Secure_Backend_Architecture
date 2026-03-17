import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import database.models  # noqa: F401
from database.test_config import test_engine, TestSessionLocal
from database.config import Base


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """ Create all tables at the beginning of the test session, then delete
    them at the end """

    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Provides an isolated SQLAlchemy session for each test.
    At the end of the test:
    - rollback if needed
    - session closure
    - complete table cleanup
    """

    session = TestSessionLocal()

    try:
        yield session
        session.rollback()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()

        with test_engine.connect() as connection:
            trans = connection.begin()
            try:
                connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

                # Supprimer le contenu de toutes les tables en ordre inverse
                for table in reversed(Base.metadata.sorted_tables):
                    connection.execute(text(f"TRUNCATE TABLE {table.name};"))

                connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
                trans.commit()
            except Exception:
                trans.rollback()
                raise


@pytest.fixture(scope="function")
def role_sales(db_session):
    from database.models import Role

    role = Role(name="commercial")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture(scope="function")
def role_support(db_session):
    from database.models import Role

    role = Role(name="support")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture(scope="function")
def sales_employee(db_session, role_sales):
    from database.models import Employee

    employee = Employee(
        full_name="Alice Martin",
        email="alice@example.com",
        password_hash="hashed_password_123",
        is_active=True,
        role_id=role_sales.role_id,
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee


@pytest.fixture(scope="function")
def support_employee(db_session, role_support):
    from database.models import Employee

    employee = Employee(
        full_name="Bob Support",
        email="bob@example.com",
        password_hash="hashed_password_456",
        is_active=True,
        role_id=role_support.role_id,
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee


@pytest.fixture(scope="function")
def customer(db_session, sales_employee):
    from database.models import Customer

    customer = Customer(
        full_name="Client Test",
        email="client@example.com",
        phone="0601020304",
        company_name="Test Company",
        sales_id=sales_employee.employee_id,
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture(scope="function")
def contract(db_session, customer):
    from database.models import Contract

    contract = Contract(
        total_amount=5000.00,
        remaining_amount=2500.00,
        is_signed=False,
        customers_id=customer.customer_id,
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)
    return contract
