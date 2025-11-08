from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from db import Base

# Enums
class CategoryType(enum.Enum):
    EXPENSE = "expense"
    INCOME = "income"

# User Model
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}')>"

# Category Model
class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(CategoryType), nullable=False, default=CategoryType.EXPENSE)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    
    def __repr__(self):
        return f"<Category(category_id={self.category_id}, name='{self.name}')>"

# Transaction Model
class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete='CASCADE'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete='SET NULL'), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    merchant = Column(String(100), nullable=True)
    date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(transaction_id={self.transaction_id}, amount={self.amount}, date='{self.date}')>"
