from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean, Table, JSON, Index
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from db import Base

# Enums
class CategoryType(enum.Enum):
    EXPENSE = "expense"
    INCOME = "income"
    INVESTMENT = "investment"

class BudgetPeriod(enum.Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class GoalStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Association table for many-to-many relationship between Transaction and Tag
transaction_tags = Table(
    'transaction_tags',
    Base.metadata,
    Column('transaction_id', Integer, ForeignKey('transactions.transaction_id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.tag_id', ondelete='CASCADE'), primary_key=True)
)

# User Model
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship(
        "Transaction",
        foreign_keys="[Transaction.user_id]",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="user", cascade="all, delete-orphan")
    networth_snapshots = relationship("NetWorthSnapshot", back_populates="user", cascade="all, delete-orphan")
    analytics_cache = relationship("AnalyticsCache", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', email='{self.email}')>"

# Account Model
class Account(Base):
    __tablename__ = "accounts"
    
    account_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete='CASCADE'), nullable=False, index=True)
    account_name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # e.g., 'savings', 'current', 'credit_card', 'fixed_deposit', 'ppf', 'nps'
    institution = Column(String(100), nullable=True)  # Bank name (e.g., SBI, HDFC, ICICI, Axis)
    balance = Column(Float, default=0.0, nullable=False)
    currency = Column(String(3), default="INR", nullable=False)  # Default to INR for Indian users
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Account(account_id={self.account_id}, account_name='{self.account_name}', type='{self.type}', balance={self.balance})>"

# Category Model
class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(CategoryType), nullable=False)  # expense/income/investment
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")
    
    def __repr__(self):
        return f"<Category(category_id={self.category_id}, name='{self.name}', type='{self.type.value}')>"

# Transaction Model
class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete='CASCADE'), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id", ondelete='CASCADE'), nullable=False, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    merchant = Column(String(150), nullable=True)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(String(50), nullable=True)
    recurrence_end_date = Column(DateTime, nullable=True)
    is_imported = Column(Boolean, default=False, nullable=False)
    import_source = Column(String(100), nullable=True)
    import_reference = Column(String(100), nullable=True)
    is_edited = Column(Boolean, default=False, nullable=False)
    last_edited_at = Column(DateTime, nullable=True)
    last_edited_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Add index for common queries
    __table_args__ = (
        Index('idx_transaction_user_date', 'user_id', 'date'),
        Index('idx_transaction_user_category', 'user_id', 'category_id'),
    )
    description = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete='SET NULL'), nullable=True, index=True)
    is_manual = Column(Boolean, default=True, nullable=False)  # True if manually entered, False if imported
    is_investment = Column(Boolean, default=False, nullable=False)  # True if it's an investment transaction
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="transactions")
    last_editor = relationship("User", foreign_keys=[last_edited_by])
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    tags = relationship("Tag", secondary=transaction_tags, back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(transaction_id={self.transaction_id}, date='{self.date}', merchant='{self.merchant}', amount={self.amount})>"

# Budget Model
class Budget(Base):
    __tablename__ = "budgets"
    
    budget_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete='CASCADE'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete='CASCADE'), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    period = Column(Enum(BudgetPeriod), nullable=False)  # monthly/yearly
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")
    
    def __repr__(self):
        return f"<Budget(budget_id={self.budget_id}, amount={self.amount}, period='{self.period.value}', start_date='{self.start_date}', end_date='{self.end_date}')>"

# Goal Model
class Goal(Base):
    __tablename__ = "goals"
    
    goal_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0, nullable=False)
    deadline = Column(DateTime, nullable=True)
    status = Column(Enum(GoalStatus), default=GoalStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    
    def __repr__(self):
        return f"<Goal(goal_id={self.goal_id}, name='{self.name}', target_amount={self.target_amount}, current_amount={self.current_amount}, status='{self.status.value}')>"

# Tag Model
class Tag(Base):
    __tablename__ = "tags"
    
    tag_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete='CASCADE'), nullable=False, index=True)
    label = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="tags")
    transactions = relationship("Transaction", secondary=transaction_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(tag_id={self.tag_id}, label='{self.label}')>"

# Investment Model
class Investment(Base):
    __tablename__ = "investments"
    
    investment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    type = Column(String(50), nullable=False)  # e.g., 'stocks', 'bonds', 'mutual_funds', 'real_estate'
    amount = Column(Float, nullable=False)  # Initial investment amount
    date = Column(DateTime, nullable=False)  # Date of investment
    current_value = Column(Float, nullable=True)  # Current market value
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="investments")
    
    def __repr__(self):
        return f"<Investment(investment_id={self.investment_id}, name='{self.name}', type='{self.type}', amount={self.amount}, current_value={self.current_value})>"

# NetWorthSnapshot Model
class NetWorthSnapshot(Base):
    __tablename__ = "networth_snapshots"
    
    snapshot_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete='CASCADE'), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    total_assets = Column(Float, nullable=False)
    total_liabilities = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="networth_snapshots")
    
    @property
    def net_worth(self):
        """Calculate net worth as assets minus liabilities"""
        return self.total_assets - self.total_liabilities
    
    def __repr__(self):
        return f"<NetWorthSnapshot(snapshot_id={self.snapshot_id}, date='{self.date}')>"

# AnalyticsCache Model
class AnalyticsCache(Base):
    """Cached analytics data for improved performance."""
    __tablename__ = "analytics_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    cache_key = Column(String(255), nullable=False, index=True)
    data = Column(JSON, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_analytics_user_key', 'user_id', 'cache_key', unique=True),
    )
    
    user = relationship("User", back_populates="analytics_cache")
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<AnalyticsCache(id={self.id}, key='{self.cache_key[:20]}...', expires='{self.expires_at}')>"
