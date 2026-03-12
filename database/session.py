from sqlalchemy.orm import sessionmaker
from database.config import engine


SessionLocal = sessionmaker(bind=engine)
