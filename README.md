# Epic Events CRM (CLI)
Command-line CRM built with:
- Python
- SQLAlchemy
- MySQL
- JWT Authentication
- Service-based architecture

This project allows to manage:
- Employees
- Customers
- Contracts
- Events
- User authentication

## Installation
1. Clone the repository `git clone https://github.com/GitDrinou/DA_Python_P12_Secure_Backend_Architecture.git`
2. Install dependencies `pipenv install`
3. Activate the virtual environment `pipenv shell`

## Configuration
Create a `.env`file.
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
```

## Database initialization
`python create_db.py`

## CRM Commands
### Authentification
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
Optional for activate or not `--inactive`
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
python customers.py update 
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
- Update contract  
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

## Technologies
- Python
- SQLAlchemy
- MySQL
- JWT
- argparse
- Service architecture
