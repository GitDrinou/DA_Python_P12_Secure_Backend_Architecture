from security.rbac import seed_rbac
from services.contract_service import ContractService
from services.customer_service import CustomerService
from services.employee_service import EmployeeService


def test_create_contract(db_session):
    seed_rbac(db_session)
    service_employee = EmployeeService(db_session)
    service_customer = CustomerService(db_session)
    service_contract = ContractService(db_session)

    sales_employee = service_employee.create_employee(
        full_name="Jean Dupont",
        email="jean.dupont@example.com",
        password="Password123!",
        role_name="commercial",
    )

    customer = service_customer.create_customer(
        full_name="Jean Dupont",
        email="jean.dupont@example.com",
        phone="123-456-7890",
        company_name="Jean TestCompany",
        current_employee=sales_employee,
    )

    manager_employee = service_employee.create_employee(
        full_name="Manager Test",
        email="manager@example.com",
        password="Password123!",
        role_name="gestion",
    )

    contract = service_contract.create_contract(
        current_employee=manager_employee,
        customer_id=customer.customer_id,
        total_amount="2000.00",
        remaining_amount="1000.00",
        is_signed=False,
    )

    assert contract.contract_id is not None
    assert contract.total_amount == 2000.00
    assert contract.customers_id == customer.customer_id
    assert contract.customer.sales_id == sales_employee.employee_id


def test_update_contract_remaining_amount(db_session, contract):
    seed_rbac(db_session)
    service = ContractService(db_session)

    sales_employee = (
        EmployeeService(db_session)
        .get_employee(employee_id=contract.customer.sales_id))

    print("EMPLOYEE: ", sales_employee.role.name)

    updated = service.update_contract(
        contract_id=contract.contract_id,
        current_employee=sales_employee,
        remaining_amount="0.00",
    )

    assert updated.remaining_amount == 0.00
