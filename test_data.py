from datetime import datetime, timezone
from decimal import Decimal
from database.models import Employee, Customer, EmployeeRole, Contract, Event
from database.session import SessionLocal
import database.models as models

session = SessionLocal()

# Create a sales employee
existing_sales_employee = session.query(Employee).filter_by(
    email="b.boquet@epic.com").first()

if not existing_sales_employee:
    sales_employee = models.Employee(
        full_name="Bill Boquet",
        email="b.boquet@epic.com",
        password_hash="hashed_password",
        role=EmployeeRole.SALES
    )

    session.add(sales_employee)
    session.commit()
else:
    print("Sales employee already exists")

# Create a support employee
existing_support_employee = session.query(Employee).filter_by(
    email="k.astroff@epic.com").first()

if not existing_support_employee:
    support_employee = models.Employee(
        full_name="Kat Astroff",
        email="k.astroff@epic.com",
        password_hash="hashed_password",
        role=EmployeeRole.SUPPORT
    )

    session.add(support_employee)
    session.commit()
else:
    print("Sales employee already exists")

# Create a customer
sales = (session.query(Employee)
         .filter(Employee.role == EmployeeRole.SALES)
         .first())
existing_customer = session.query(Customer).filter_by(
    email="jessie983@mail.com").first()

if not existing_customer:
    customer = models.Customer(
        full_name="Jessie James",
        email="jessie983@mail.com",
        phone="0601010101",
        company_name="ACME Corp",
        sales_id=sales.id
    )

    session.add(customer)
    session.commit()
else:
    print("Customer already exists")

# Create a contract for a client
customer = session.query(Customer).first()
contract = models.Contract(
    total_amount=Decimal("5000.00"),
    remaining_amount=Decimal("5000.00"),
    customers_id=customer.id
)

session.add(contract)
session.commit()

# Create an event
contract = session.query(Contract).first()
support = (session.query(Employee)
           .filter(Employee.role == EmployeeRole.SUPPORT)
           .first())
event = models.Event(
    title="Annual Conference",
    end_date=datetime(2026, 6, 10, 18, 0, tzinfo=timezone.utc),
    location="53 Rue de la boétie, 75008 Paris, France",
    attendees=200,
    notes="The conference starts at 8AM with a breakfast. Lunch at 12AM. "
          "End at 6PM with soft beverage and vegetarian meals.",
    contract_id=contract.id,
    support_id=support.id
)

session.add(event)
session.commit()

# Read event data
event = session.query(Event).first()

print("Event: ", event.title)
print("Client: ", event.contract.customer.full_name)
print("Entreprise: ", event.contract.customer.company_name)
print("Sales: ", event.contract.customer.sales.full_name)
print("Support: ", event.support.full_name)

session.close()
