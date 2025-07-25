from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.core.config import get_settings

settings = get_settings()

# Use the appropriate database URL
database_url = settings.get_database_url()
engine = create_engine(
    database_url,
    # SQLite specific settings
    connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()