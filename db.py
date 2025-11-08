from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///finco.db')

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
    pool_pre_ping=True
)

# Create declarative base
Base = declarative_base()

# Create session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database with default data"""
    # Import models here to avoid circular imports
    from models import User, Category, CategoryType
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create default categories if they don't exist
    db = SessionLocal()
    try:
        if not db.query(Category).first():
            # Create default user
            default_user = User(
                username="default",
                email="user@example.com",
                hashed_password=""
            )
            db.add(default_user)
            db.flush()
            
            # Add default categories
            default_categories = [
                "Food & Dining", "Shopping", "Transportation", "Housing",
                "Utilities", "Entertainment", "Health", "Other"
            ]
            
            for cat_name in default_categories:
                db.add(Category(
                    user_id=default_user.user_id,
                    name=cat_name,
                    type=CategoryType.EXPENSE
                ))
            
            db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Alias for backward compatibility
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
