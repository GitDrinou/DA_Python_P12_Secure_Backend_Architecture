import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

db_user = os.getenv("MYSQL_USER")
db_password = os.getenv("MYSQL_USER_PASSWORD")
db_host = os.getenv("MYSQL_HOST", "localhost")
db_port = int(os.getenv("MYSQL_PORT", "3306"))
db_name = os.getenv("MYSQL_DATABASE")

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=db_user,
    password=db_password,
    host=db_host,
    port=db_port,
    database=db_name,
)

engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()

print("MYSQL_USER =", db_user)
print("MYSQL_HOST =", db_host)
print("MYSQL_PORT =", db_port)
print("MYSQL_DATABASE =", db_name)
print("MYSQL_PASSWORD défini =", db_password is not None)
