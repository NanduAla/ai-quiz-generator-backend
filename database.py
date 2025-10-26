# backend/database.py

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Database Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://user:password@localhost/quizdb"

# ✅ Fix Render's 'postgres://' URL format issue
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 1. Create SQLAlchemy Engine
engine = create_engine(DATABASE_URL, echo=False)

# 2. Create Declarative Base Class
Base = declarative_base()

# 3. Define the Quiz Model
class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    date_generated = Column(DateTime, default=func.now())
    full_quiz_data = Column(Text, nullable=False)
    scraped_content = Column(Text, nullable=True)

# 4. Session Local Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Helper function to create tables
def init_db():
    """Initializes the database and creates all tables."""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully.")
    except Exception:
        print("⚠️ Database initialization failed.")

# 6. Dependency for FastAPI to get a database session
def get_db():
    """Yields a database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
