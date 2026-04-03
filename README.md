# Epic Events CRM (CLI)
## Project Overview
Epic Events CRM is a secure command-line application designed to manage 
clients, contracts, events and employees for the Epic Events company.

The application is built with Python and follows secure backend development 
practices, including role-based access control and structured logging.

The project follows secure backend architecture principles:
- Role-based access control
- JWT authentication
- Service-based architecture
- Logging and observability
- Principle of least privilege

## Project Architecture
The project follows a Service-based layered architecture:
1. Presentation Layer
2. Business Logic Layer
3. Data Access Layer
4. Database
### Architecture Components
- CLI > Handles user input and commands
- Services > contains business logic
- Permissions > role-based access control
- Database > SQLAlchemy models & database configuration
- Observability > error logging & monitoring

## Features
- Secure authentication (JWT)
- Role-based permissions
- Customer management
- Contract management
- Event management
- Command-line interface
- Logging & observability
- Secure backend architecture

## Roles & Permissions
Epic Events is organized in 3 departments:

### Sales Team
Sales users manage customers and contracts.
#### Permissions
- Create customers
- Update / Delete their customers
- Update contracts of their customers
- Create events if signed contract
- View all data

### Management Team
Management users have administrative permissions.
#### Permissions
- Create / Update / Dealete employees
- Create / Update contracts
- Assign support to events
- View all data

### Support
Support users manage events assigned to them.
#### Permissions
- View assigned events
- Update assigned events
- View all data

## Application Workflow
1. Sales creates customer 
2. Management creates contract 
3. Contract is signed 
4. Sales creates event 
5. Management assigns support 
6. Support manages event


## Database Configuration
The application requires 2 separate databases:
- 1 database for the application
- 1 database for tests
### Environment variables
Environment variables are managed using 2 files:
- `.env` for application configuration

Example:
```
MYSQL_USER=your_db_user
MYSQL_USER_PASSWORD=your_db_user_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=epic_events_db

JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_ISSUER=epic-events-crm
REFRESH_TOKEN_EXPIRE_DAYS=7

SENTRY_DSN=my-sentry-dsn
SENTRY_ENVIRONMENT=development
SENTRY_RELEASE=epic-events-crm@1.0.0

CRM_ADMIN_USER_EMAIL=admin@epic-events.com
CRM_ADMIN_USER_PASSWORD=securepassword
```
- `.env.test` for test configuration

Example:
```
MYSQL_USER=your_db_user
MYSQL_USER_PASSWORD=your_db_user_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=epic_events_test_db

JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_ISSUER=epic-events-crm
REFRESH_TOKEN_EXPIRE_DAYS=7

SENTRY_DSN=
SENTRY_ENVIRONMENT=test
```
Using a dedicated test database ensures that tests do not affect production 
or development data

## Installation
1. Clone the repository `git clone https://github.com/GitDrinou/DA_Python_P12_Secure_Backend_Architecture.git`
2. Create a virtual environment by running the following lines in your terminal:
   - first, go the application's root directory
   - check if you have access to venv: `python -m venv --help`
   - create the environment with : `python -m venv env`
   - activate the environment with:
     - for MacOS/Linux: `source env/bin/activate`
     - for Windows: `env\Scripts\activate`
   - Install the required packages with : `pip install -r requirements.txt`
3. Create your .env and .env-test files based on the examples above.
4. Initialize the database with this command `python create_db.py`

If you use ***pipenv***: 
1. Install dependencies `pipenv install`
2. Activate the virtual environment `pipenv shell`
3. Create your .env and .env-test files based on the examples above.
4. Initialize the database with this command `python create_db.py`


## Usage / CRM Commands
### Commands help
For each resource you can access to the help documentation.

Example: ```python epic_events.py --help```
will display the commands definitions for the `epic_events.py` 
authentication resource.

### Authentication
- Login `python epic_events.py login --email EMAIL --password PASSWORD`
- Logout `python epic_events.py logout`
- Current user `python epic_events.py whoami`

### Employees
- List employees `python employees.py list`
- Get employee details `python employees.py get --employee-id ID`
- Create employee  
```
python employees.py create 
    --full-name "EMPLOYEE NAME" 
    --email EMPLOYEE@MAIL.COM 
    --password PASSWORD 
    --role ROLE
```
Optional flag: `--inactive` to create the employee as inactive.
- Update employee  
```
python employees.py update 
    --employee-id ID
    --full-name "EMPLOYEE NAME" 
    --email EMPLOYEE@MAIL.COM 
    --password PASSWORD 
    --role ROLE
    --is-active TRUE or FALSE
```
- Delete employee `python employees.py delete --employee-id ID`

### Customers
- List customers `python customers.py list`
- Get customer details `python customers.py get --customer-id ID`
- Create customer  
```
python customers.py create 
    --full-name "CUSTOMER NAME" 
    --email CUSTOMER@MAIL.COM 
    --phone "0000000000" 
    --company-name "COMPANY"
```
- Update customer  
```
python customers.py update 
    --customer-id ID
    --full-name "CUSTOMER NAME" 
    --email CUSTOMER@MAIL.COM 
    --phone "0000000000" 
    --company-name "COMPANY"
```

### Contracts
- List all contracts `python contracts.py list`
- Filter contracts unsigned or unpaid `python contracts.py list 
--unsigned-or-unpaid`
- Get contract details `python contracts.py get --contract-id ID`
- Create contract  
```
python contracts.py create 
    --customer-id ID 
    --total-amount "1000" 
    --remaining-amount "500" 
    --is-signed FALSE
```
- Update contract  
```
python contracts.py update 
    --contract-id ID
    --total-amount "1000" 
    --remaining-amount "500" 
    --is-signed TRUE
```

### Events
- List all events `python events.py list`
- Filter events without support `python events.py list --without-support`
- Filter events assigned to me `python events.py list --assigned-to-me`
- Get event details `python events.py get --event-id ID`
- Create event  
```
python events.py create 
    --contract-id ID 
    --title "EVENT TITLE" 
    --start-date "01/01/2024" 
    --end-date "01/01/2024" 
    --location "LOCATION" 
    --attendees 50 
    --notes "NOTES"
```
- Update event  
```
python events.py update 
    --event-id ID 
    --title "EVENT TITLE" 
    --start-date "01/01/2024" 
    --end-date "01/01/2024" 
    --location "LOCATION" 
    --attendees 50 
    --notes "NOTES"
```
- Assign support
```
python events.py assign-support 
    --event-id ID 
    --support-id ID
```

## Security
The application implements multiple security layers:
### Authentication
- JWT authentication
- Token expiration
- Secure login/logout
### Authorization
- Role-based access control
- Principle of least privilege
- Permission decorators
### Database Security
- SQLAlchemy ORM
- Protection against SQL injection
### Logging
- Observability module
- Exception tracking
- Error logging

## Tech Stack
- Python
- SQLAlchemy
- MySQL
- JWT
- Argon2
- Click & Rich
- Sentry

## Running Test
This project uses **pytest** with coverage reporting.

Run the full test and generates coverage reports: `pytest`

### Pytest options
The project uses the following pytest options:
- `-v`: verbose mode
- `--cov`: enable coverage measurement
- `--cov-report=term-missing`: coverage report in terminal with missing lines
- `--cov-report=html`: generate HTML coverage report
- `--cov-report=wml`: generate XML coverage report

Example: `pytest -v --cov --cov-report=term-missing --cov-report=html --cov-report=xml`

## Code Quality
This project follows strict code quality standards enforced with Flake8.
Flake8 is used to ensure consistency, readability, and maintainability 
across the codebase.

Before committing changes, you should use the command: `flake8`

If any issues are detected, they should be fixed before pushing code. This 
helps maintain a clean and consistent codebase across contribution.
