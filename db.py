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

# Create a scoped session
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# Base class for declarative models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import all models here to ensure they are registered with SQLAlchemy
    from models import User, Category, Transaction
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create default categories if they don't exist
    db = SessionLocal()
    try:
        # Check if we have any categories
        if not db.query(Category).first():
            # Create a default user
            default_user = User(
                username="default",
                email="user@example.com",
                hashed_password=""  # Password should be hashed in a real app
            )
            db.add(default_user)
            db.flush()  # To get the user_id
            
            # Default expense categories
            default_categories = [
                "Food & Dining",
                "Shopping",
                "Transportation",
                "Housing",
                "Utilities",
                "Entertainment",
                "Health",
                "Other"
            ]
            
            # Add default categories
            for cat_name in default_categories:
                category = Category(
                    user_id=default_user.user_id,
                    name=cat_name,
                    type=CategoryType.EXPENSE
                )
                db.add(category)
            
            db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Alias for get_db for backward compatibility
get_db_session = get_db

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
