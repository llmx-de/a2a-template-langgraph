import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Load the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://a2a_service:a2a_service@localhost:5488/a2a_service")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative class definitions
Base = declarative_base()

# Dependency function for FastAPI routes to get a session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 