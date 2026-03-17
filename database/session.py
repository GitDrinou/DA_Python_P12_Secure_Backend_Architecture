from sqlalchemy.orm import sessionmaker
from database.config import engine


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)
