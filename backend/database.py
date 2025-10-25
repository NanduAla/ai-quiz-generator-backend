# backend/database.py

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv # REMOVED: Now loaded centrally in main.py

# load_dotenv() # REMOVED: Now loaded centrally in main.py

# --- Database Configuration ---
# NOTE: Using PostgreSQL as per the assignment requirement (or MYSQL).
# Replace with your actual connection string (e.g., from an environment variable)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/quizdb")

# 1. Create SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    echo=False # Set to True to see SQL logs
)

# 2. Create Declarative Base Class
Base = declarative_base()

# 3. Define the Quiz Model
class Quiz(Base):
    """
    SQLAlchemy model for storing quiz history.
    The complex JSON output is stored as a TEXT field.
    """
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    date_generated = Column(DateTime, default=func.now())
    
    # CRUCIAL: Store the full JSON output from the LLM after serialization (json.dumps)
    full_quiz_data = Column(Text, nullable=False) 
    
    # Optional Bonus field
    scraped_content = Column(Text, nullable=True) 

# 4. Session Local Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Helper function to create tables (Run this once on startup)
def init_db():
    """Initializes the database and creates all tables."""
    Base.metadata.create_all(bind=engine)

# 6. Dependency for FastAPI to get a database session
def get_db():
    """Yields a database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()