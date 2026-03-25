import pytest
from decimal import Decimal
from security.permissions import ROLE_MANAGEMENT, ROLE_SALES, ROLE_SUPPORT
from security.rbac import seed_rbac
from services.contract_service import ContractService
from tests.factories import create_employee, create_customer, create_contract


def test_manager_can_create_any_contract(db_session):
    seed_rbac(db_session)
    service = ContractService(db_session)

    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager",
        email="manager@test.com",
    )
    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com",
    )
    customer = create_customer(
        db_session,
        sales,
        email="customer@test.com",
    )

    contract = service.create_contract(
        current_employee=manager,
        customer_id=customer.customer_id,
        total_amount="1000.00",
        remaining_amount="1000.00",
        is_signed=False,
    )

    assert contract is not None
    assert contract.total_amount == Decimal("1000.00")
    assert contract.remaining_amount == Decimal("1000.00")
    assert contract.is_signed is False
    assert contract.customers_id == customer.customer_id


def test_sales_cannot_create_contract(db_session):
    seed_rbac(db_session)
    service = ContractService(db_session)

    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com",
    )

    customer = create_customer(
        db_session,
        sales,
        email="customer@test.com"
    )

    with pytest.raises(
            ValueError,
            match="You are not allowed to create contracts"
    ):
        service.create_contract(
            current_employee=sales,
            customer_id=customer.customer_id,
            total_amount="1000.00",
            remaining_amount="1000.00",
        )


def test_create_contract_customer_not_found(db_session):
    seed_rbac(db_session)
    service = ContractService(db_session)

    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager",
        email="manager@test.com",
    )

    with pytest.raises(ValueError, match="Customer not found"):
        service.create_contract(
            current_employee=manager,
            customer_id="unknown",
            total_amount="1000.00",
            remaining_amount="1000.00",
        )


def test_create_contract_negative_total_amount(db_session):
    seed_rbac(db_session)
    service = ContractService(db_session)

    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager",
        email="manager@test.com",
    )
    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com",
    )
    customer = create_customer(
        db_session,
        sales,
        email="customer@test.com"
    )

    with pytest.raises(ValueError, match="Total amount cannot be negative"):
        service.create_contract(
            current_employee=manager,
            customer_id=customer.customer_id,
            total_amount="-1000.00",
            remaining_amount="-1000.00",
        )


def test_create_contract_remaining_greater_than_total_amount(db_session):
    seed_rbac(db_session)
    service = ContractService(db_session)

    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager",
        email="manager@test.com",
    )
    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com",
    )
    customer = create_customer(
        db_session,
        sales,
        email="customer@test.com",
    )

    with pytest.raises(
            ValueError,
            match="Remaining amount cannot exceed total amount"
    ):
        service.create_contract(
            current_employee=manager,
            customer_id=customer.customer_id,
            total_amount="1000.00",
            remaining_amount="2000.00",
        )


def test_manager_can_update_any_contract(db_session):
    seed_rbac(db_session)
    service = ContractService(db_session)
    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager",
        email="manager@test.com",
    )
    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com",
    )
    customer = create_customer(
        db_session,
        sales,
        email="customer@test.com",
    )
    contract = create_contract(
        db_session,
        customer,
        total="1000.00",
        remaining="1000.00",
    )

    updated = service.update_contract(
        contract_id=contract.contract_id,
        current_employee=manager,
        total_amount="1000.00",
        remaining_amount="500.00",
        is_signed=True,
    )

    assert updated.total_amount == Decimal("1000.00")
    assert updated.remaining_amount == Decimal("500.00")
    assert updated.is_signed is True


def test_sales_can_update_contract_of_owned_customer(db_session):
    seed_rbac(db_session)
    service = ContractService(db_session)

    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com",
    )
    customer = create_customer(
        db_session,
        sales,
        email="owned-customer@test.com"
    )
    contract = create_contract(
        db_session,
        customer,
        total="2000.00",
        remaining="1200.00",
    )

    update = service.update_contract(
        contract_id=contract.contract_id,
        current_employee=sales,
        remaining_amount="0.00",
        is_signed=True,
    )

    assert update.remaining_amount == Decimal("0.00")
    assert update.is_signed is True


def test_sales_cannot_update_contrac_of_other_sales_customer(db_session):
    seed_rbac(db_session)
    service = ContractService(db_session)
    sales_alice = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales Alice",
        email="sales-alice@test.com",
    )
    sales_bob = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales Bob",
        email="sales-bob@test.com",
    )
    sales_bob_customer = create_customer(
        db_session,
        sales_bob,
        email="bob-customer@test.com",
    )

    contract = create_contract(
        db_session,
        sales_bob_customer,
        total="1000.00",
        remaining="1000.00",
        is_signed=True,
    )

    with pytest.raises(
            ValueError,
            match="You are not allowed to update this contract"
    ):
        service.update_contract(
            contract_id=contract.contract_id,
            current_employee=sales_alice,
            remaining_amount="100.00",
        )


def test_support_cannot_update_contract(db_session):
    seed_rbac(db_session)
    service = ContractService(db_session)

    support = create_employee(
        db_session,
        ROLE_SUPPORT,
        full_name="Support",
        email="support@test.com",
    )
    sales = create_employee(
        db_session,
        ROLE_SALES,
        full_name="Sales",
        email="sales@test.com",
    )
    customer = create_customer(
        db_session,
        sales,
        email="customer@test.com"
    )
    contract = create_contract(
        db_session,
        customer
    )

    with pytest.raises(
        ValueError,
        match="You are not allowed to update this contract"
    ):
        service.update_contract(
            contract_id=contract.contract_id,
            current_employee=support,
            remaining_amount="100.00",
        )


def test_update_contract_raises_if_contract_not_found(db_session):
    seed_rbac(db_session)
    service = ContractService(db_session)

    manager = create_employee(
        db_session,
        ROLE_MANAGEMENT,
        full_name="Manager",
        email="manager@test.com",
    )

    with pytest.raises(ValueError, match="Contract not found"):
        service.update_contract(
            contract_id="unknown-contract-id",
            current_employee=manager,
            remaining_amount="100.00",
        )
