from database.models import Customer
from sqlalchemy.orm import joinedload
from security.authorization import can_update_customer, can_delete_customer


class CustomerService:
    def __init__(self, db_session):
        self.db_session = db_session

    def list_customers(self):
        """ List all customers """
        return (
            self.db_session.query(Customer)
            .options(joinedload(Customer.sales))
            .order_by(Customer.full_name.asc())
            .all()
        )

    def get_customer(self, customer_id):
        """
        Get customer by customer id
        Args:
            customer_id (str): customer ident
        """
        customer = (
            self.db_session.query(Customer)
            .options(joinedload(Customer.sales))
            .filter(Customer.customer_id == customer_id)
            .first()
        )

        if customer is None:
            raise ValueError("Customer not found")

        return customer

    def create_customer(
            self,
            current_employee,
            full_name,
            email,
            phone,
            company_name
    ):
        """
        Create new customer
        Args:
            current_employee (object)
            full_name (str): customer full name
            email (str): customer email
            phone (str): customer phone number
            company_name (str): customer company name
        """
        from security import has_permission
        from security.permissions import PERM_CUSTOMERS_CREATE_OWNED

        if not has_permission(current_employee,
                              PERM_CUSTOMERS_CREATE_OWNED):
            raise ValueError("You are not allowed to create customer")

        existing = (
            self.db_session.query(Customer)
            .filter(Customer.email == email)
            .first()
        )
        if existing:
            raise ValueError("Customer already exists")

        customer = Customer(
            full_name=full_name,
            email=email,
            phone=phone,
            company_name=company_name,
            sales_id=current_employee.employee_id,
        )

        self.db_session.add(customer)
        self.db_session.commit()
        self.db_session.refresh(customer)

        return customer

    def update_customer(
            self,
            current_employee,
            customer_id,
            full_name=None,
            email=None,
            phone=None,
            company_name=None,
    ):
        """
        Update customer details
        Args:
           current_employee (object)
           customer_id (str): customer id
           full_name (str): customer full name
           email (str): customer email
           phone (str): customer phone number
           company_name (str): customer company name
        """
        customer = self.get_customer(customer_id)

        if not can_update_customer(current_employee, customer):
            raise ValueError("You are not allowed to update customer")

        if full_name is not None:
            customer.full_name = full_name
        if email is not None:
            customer.email = email
        if phone is not None:
            customer.phone = phone
        if company_name is not None:
            customer.company_name = company_name

        self.db_session.commit()
        self.db_session.refresh(customer)

        return customer

    def delete_customer(self, current_employee, customer_id):
        """
        Delete customer by customer id
        Args:
            current_employee (object)
            customer_id (str): customer id
        """
        customer = self.get_customer(customer_id)

        if not can_delete_customer(current_employee, customer):
            raise ValueError("You are not allowed to delete customer")

        self.db_session.delete(customer)
        self.db_session.commit()

        return True
