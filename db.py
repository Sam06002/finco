from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import database_exists, create_database
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
# Default to local SQLite database if not specified
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///finance.db")

# Create SQLAlchemy engine
# For SQLite, we need to set check_same_thread to False to allow multiple threads
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,  # Set to True for SQL query logging during development
    pool_pre_ping=True  # Verify connections before using them
)

# Create database if it doesn't exist (for SQLite and PostgreSQL)
if not database_exists(engine.url):
    create_database(engine.url)
    print(f"Created database at: {DATABASE_URL}")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()

def init_db():
    """
    Initialize the database by creating all tables.
    Import all models before calling this function.
    """
    # Import all models here to ensure they are registered with Base
    from models import (
        User, Account, Category, Transaction, 
        Budget, Goal, Tag, Investment, NetWorthSnapshot
    )
    
    # Create all tables in the database
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def get_db():
    """
    Dependency function to get DB session (generator pattern).
    Use this with FastAPI or in contexts where you need a generator.
    
    Usage:
        for db in get_db():
            # use db session
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session() -> Session:
    """
    Get a new database session.
    Remember to close the session after use.
    
    Usage:
        db = get_db_session()
        try:
            # use db session
            user = db.query(User).first()
        finally:
            db.close()
    
    Or use with context manager:
        with get_db_session() as db:
            # use db session
            user = db.query(User).first()
    """
    return SessionLocal()

class DatabaseSession:
    """
    Context manager for database sessions.
    Automatically handles commit, rollback, and close.
    
    Usage:
        with DatabaseSession() as db:
            user = User(username="john", email="john@example.com")
            db.add(user)
            # Automatically commits on successful exit
    """
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self) -> Session:
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # If an exception occurred, rollback the transaction
            self.db.rollback()
        else:
            # Otherwise, commit the transaction
            self.db.commit()
        self.db.close()
        return False
