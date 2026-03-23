from sqlalchemy.orm import joinedload
from database.models import Employee, Role
from security.passwords import hash_password


class EmployeeService:
    def __init__(self, db_session):
        self.db_session = db_session

    def list_employees(self):
        """ List all employees """
        return (
            self.db_session.query(Employee)
            .options(joinedload(Employee.role))
            .order_by(Employee.full_name.asc())
            .all()
        )

    def get_employee(self, employee_id):
        """ Get employee by employee id
            Args:
                employee_id (str): employee ident
        """
        employee = (
            self.db_session.query(Employee)
            .options(joinedload(Employee.role))
            .filter(Employee.employee_id == employee_id)
            .first()
        )

        if employee is None:
            raise ValueError("Employee not found")

        return employee

    def create_employee(
            self,
            full_name,
            email,
            password,
            role_name,
            is_active=True
    ):
        """
        Create new employee
        Args:
            full_name (str): employee full name
            email (str): employee email
            password (str): employee password
            role_name (str): employee role
            is_active (bool): employee is active
        """
        role = (
            self.db_session.query(Role)
            .filter(Role.name == role_name)
            .first()
        )

        if role is None:
            raise ValueError("Role not found")

        existing = (
            self.db_session.query(Employee)
            .filter(Employee.email == email)
            .first()
        )

        if existing:
            raise ValueError("Employee already exists with this email")

        employee = Employee(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            is_active=is_active,
            role_id=role.role_id,
        )

        self.db_session.add(employee)
        self.db_session.commit()
        self.db_session.refresh(employee)

        return employee

    def update_employee(
            self,
            employee_id,
            full_name=None,
            email=None,
            password=None,
            role_name=None,
            is_active=None
    ):
        """
        Update employee by employee id
        Args:
            employee_id (str): employee ident
            full_name (str): employee full name (default None)
            email (str): employee email (default None)
            password (str): employee password (default None)
            role_name (str): employee role (default None)
            is_active (bool): employee is active (default None)
        """
        employee = self.get_employee(employee_id)

        if full_name is not None:
            employee.full_name = full_name

        if email is not None:
            existing = (
                self.db_session.query(Employee)
                .filter(
                    Employee.email == email,
                    Employee.employee_id != employee_id
                )
                .first()
            )

            if existing:
                raise ValueError("Employee already exists with this email")

            employee.email = email

        if password is not None:
            employee.password_hash = hash_password(password)

        if role_name is not None:
            role = (
                self.db_session.query(Role)
                .filter(Role.name == role_name)
                .first()
            )

            if role is None:
                raise ValueError("Role not found")

            employee.role_id = role.role_id

        if is_active is not None:
            employee.is_active = is_active

        self.db_session.commit()
        self.db_session.refresh(employee)

        return employee

    def delete_employee(self, employee_id):
        """
        Delete employee by employee id
        Args:
            employee_id (str): employee ident
        """
        employee = self.get_employee(employee_id)
        self.db_session.delete(employee)
        self.db_session.commit()

        return True
