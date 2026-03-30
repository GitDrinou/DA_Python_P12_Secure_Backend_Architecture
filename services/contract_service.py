from sqlalchemy.orm import joinedload
from decimal import Decimal
from database.models import Contract, Customer
from security import has_permission, can_update_contract
from security.permissions import PERM_CONTRACTS_CREATE_ALL, \
    PERM_CONTRACTS_FILTER_UNSIGNED_OR_UNPAID


class ContractService:
    def __init__(self, db_session):
        self.db_session = db_session

    def list_contracts(self):
        """ List all contracts """
        return (
            self.db_session.query(Contract)
            .options(joinedload(Contract.customer))
            .order_by(Contract.created_at.desc())
            .all()
        )

    def list_unsigned_or_unpaid_contracts(self, current_employee):
        """
        List all un-signed contracts
        Args:
            current_employee (Employee): current employee object
        """
        if not has_permission(current_employee,
                              PERM_CONTRACTS_FILTER_UNSIGNED_OR_UNPAID):
            raise ValueError(
                "You are not allowed to list unsigned or unpaid contracts"
            )

        return (
            self.db_session.query(Contract)
            .options(joinedload(Contract.customer))
            .filter(
                (Contract.is_signed.is_(False)) |
                (Contract.remaining_amount > 0)
            )
            .order_by(Contract.created_at.desc())
            .all()
        )

    def get_contract(self, contract_id):
        """
        Get contract by contract_id
        Args:
            contract_id (str): contract id
        """
        contract = (
            self.db_session.query(Contract)
            .options(joinedload(Contract.customer))
            .filter(Contract.contract_id == contract_id)
            .first()
        )

        if contract is None:
            raise ValueError("Contract not found")

        return contract

    def create_contract(
            self,
            current_employee,
            customer_id,
            total_amount,
            remaining_amount,
            is_signed=False,
    ):
        """
        Create a new contract
        Args:
            current_employee (Employee): current employee object
            customer_id (str): (required) customer id
            total_amount (str): (required) total amount
            remaining_amount (str): (required) remaining amount
            is_signed (boolean): (optional) signed or unsigned
        """
        if not has_permission(current_employee, PERM_CONTRACTS_CREATE_ALL):
            raise ValueError("You are not allowed to create contract")

        customer = (
            self.db_session.query(Customer)
            .filter(Customer.customer_id == customer_id)
            .first()
        )

        if customer is None:
            raise ValueError("Customer not found")

        total_amount = Decimal(str(total_amount))
        remaining_amount = Decimal(str(remaining_amount))

        if total_amount < 0:
            raise ValueError("Total amount cannot be negative")

        if remaining_amount < 0:
            raise ValueError("Remaining amount cannot be negative")

        if remaining_amount > total_amount:
            raise ValueError("Remaining amount cannot exceed total amount")

        contract = Contract(
            customers_id=customer_id,
            total_amount=total_amount,
            remaining_amount=remaining_amount,
            is_signed=is_signed,
        )

        self.db_session.add(contract)
        self.db_session.commit()
        self.db_session.refresh(contract)

        return contract

    def update_contract(
            self,
            current_employee,
            contract_id,
            total_amount=None,
            remaining_amount=None,
            is_signed=None,
    ):
        """
        Update an existing contract
        Args:
            current_employee (Employee): current employee object
            contract_id (str): contract id
            total_amount (str): total amount
            remaining_amount (str): remaining amount
            is_signed (boolean): (optional) signed or unsigned
        """
        contract = self.get_contract(contract_id)

        if not can_update_contract(current_employee, contract):
            raise ValueError("You are not allowed to update contract")

        new_total_amount = (
            Decimal(str(total_amount))
            if total_amount is not None
            else Decimal(str(contract.total_amount))
        )
        new_remaining_amount = (
            Decimal(str(remaining_amount))
            if remaining_amount is not None
            else Decimal(str(contract.remaining_amount))
        )

        if new_total_amount < 0:
            raise ValueError("Total amount cannot be negative")

        if new_remaining_amount < 0:
            raise ValueError("Remaining amount cannot be negative")

        if new_remaining_amount > new_total_amount:
            raise ValueError("Remaining amount cannot exceed total amount")

        if total_amount is not None:
            contract.total_amount = new_total_amount
        if remaining_amount is not None:
            contract.remaining_amount = new_remaining_amount
        if is_signed is not None:
            contract.is_signed = is_signed

        self.db_session.add(contract)
        self.db_session.commit()
        self.db_session.refresh(contract)

        return contract
