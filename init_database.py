"""
Database initialization script for FinCo application.
Run this script to create all database tables and optionally seed with sample data.
"""

from db import init_db, get_db_session, DatabaseSession
from models import User, Account, Category, CategoryType, Transaction, Budget, BudgetPeriod, Goal, GoalStatus, Tag, Investment, NetWorthSnapshot
from datetime import datetime, timedelta
import os

def create_sample_data():
    """Create sample data for testing and demonstration purposes."""
    
    print("\n📝 Creating sample data...")
    
    with DatabaseSession() as db:
        # Check if data already exists
        existing_user = db.query(User).first()
        if existing_user:
            print("⚠️  Sample data already exists. Skipping...")
            return
        
        # Create a sample user
        user = User(
            username="demo_user",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: "secret"
            email="demo@finco.app"
        )
        db.add(user)
        db.flush()  # Get user_id
        
        print(f"✅ Created user: {user.username}")
        
        # Create accounts
        checking = Account(
            user_id=user.user_id,
            account_name="HDFC Savings",
            type="savings",
            institution="HDFC Bank",
            balance=52407.50,
            currency="INR"
        )
        
        savings = Account(
            user_id=user.user_id,
            account_name="SBI Fixed Deposit",
            type="fixed_deposit",
            institution="State Bank of India",
            balance=125000.00,
            currency="INR"
        )
        
        credit = Account(
            user_id=user.user_id,
            account_name="ICICI Credit Card",
            type="credit_card",
            institution="ICICI Bank",
            balance=-12503.00,
            currency="INR"
        )
        
        db.add_all([checking, savings, credit])
        db.flush()
        
        print(f"✅ Created {3} accounts")
        
        # Create categories
        categories = [
            Category(user_id=user.user_id, name="Salary", type=CategoryType.INCOME),
            Category(user_id=user.user_id, name="Food & Dining", type=CategoryType.EXPENSE),
            Category(user_id=user.user_id, name="Transportation", type=CategoryType.EXPENSE),
            Category(user_id=user.user_id, name="Housing", type=CategoryType.EXPENSE),
            Category(user_id=user.user_id, name="Entertainment", type=CategoryType.EXPENSE),
            Category(user_id=user.user_id, name="Utilities", type=CategoryType.EXPENSE),
            Category(user_id=user.user_id, name="Stocks", type=CategoryType.INVESTMENT),
        ]
        
        db.add_all(categories)
        db.flush()
        
        print(f"✅ Created {len(categories)} categories")
        
        # Create tags
        tags = [
            Tag(user_id=user.user_id, label="essential"),
            Tag(user_id=user.user_id, label="recurring"),
            Tag(user_id=user.user_id, label="one-time"),
            Tag(user_id=user.user_id, label="business"),
        ]
        
        db.add_all(tags)
        db.flush()
        
        print(f"✅ Created {len(tags)} tags")
        
        # Create sample transactions
        transactions = [
            Transaction(
                user_id=user.user_id,
                account_id=checking.account_id,
                date=datetime.now() - timedelta(days=1),
                merchant="BigBasket",
                description="Monthly Groceries",
                amount=-2850.00,
                category_id=categories[1].category_id,
                is_manual=True,
                is_investment=False
            ),
            Transaction(
                user_id=user.user_id,
                account_id=checking.account_id,
                date=datetime.now() - timedelta(days=2),
                merchant="MSEDCL",
                description="Electricity Bill - Mumbai",
                amount=-1850.00,
                category_id=categories[5].category_id,
                is_manual=False,
                is_investment=False
            ),
            Transaction(
                user_id=user.user_id,
                account_id=checking.account_id,
                date=datetime.now() - timedelta(days=5),
                merchant="Tech Corp India Pvt Ltd",
                description="Monthly Salary",
                amount=75000.00,
                category_id=categories[0].category_id,
                is_manual=False,
                is_investment=False
            ),
        ]
        
        db.add_all(transactions)
        db.flush()
        
        # Add tags to transactions
        transactions[0].tags.append(tags[0])  # essential
        transactions[1].tags.append(tags[0])  # essential
        transactions[1].tags.append(tags[1])  # recurring
        
        print(f"✅ Created {len(transactions)} transactions")
        
        # Create a budget
        budget = Budget(
            user_id=user.user_id,
            category_id=categories[1].category_id,  # Food & Dining
            amount=15000.00,
            start_date=datetime.now().replace(day=1),
            end_date=(datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
            period=BudgetPeriod.MONTHLY
        )
        
        db.add(budget)
        
        print(f"✅ Created budget for {categories[1].name}")
        
        # Create a goal
        goal = Goal(
            user_id=user.user_id,
            name="Emergency Fund (6 months)",
            target_amount=500000.00,
            current_amount=125000.00,
            deadline=datetime.now() + timedelta(days=365),
            status=GoalStatus.ACTIVE
        )
        
        db.add(goal)
        
        print(f"✅ Created goal: {goal.name}")
        
        # Create an investment
        investment = Investment(
            user_id=user.user_id,
            name="HDFC Equity Fund (SIP)",
            type="mutual_fund",
            amount=50000.00,
            date=datetime.now() - timedelta(days=90),
            current_value=57500.00
        )
        
        db.add(investment)
        
        print(f"✅ Created investment: {investment.name}")
        
        # Create a net worth snapshot
        snapshot = NetWorthSnapshot(
            user_id=user.user_id,
            date=datetime.now(),
            total_assets=checking.balance + savings.balance + investment.current_value,
            total_liabilities=abs(credit.balance)
        )
        
        db.add(snapshot)
        
        print(f"✅ Created net worth snapshot: ₹{snapshot.net_worth:,.2f}")
        
        print("\n✨ Sample data created successfully!")

def main():
    """Main function to initialize the database."""
    
    print("=" * 50)
    print("🚀 FinCo Database Initialization")
    print("=" * 50)
    
    # Initialize database (create all tables)
    print("\n🔨 Creating database tables...")
    init_db()
    
    # Ask user if they want to create sample data
    response = input("\n❓ Would you like to create sample data? (y/n): ").lower().strip()
    
    if response == 'y' or response == 'yes':
        create_sample_data()
    else:
        print("\n✅ Database initialized without sample data.")
    
    print("\n" + "=" * 50)
    print("✨ Database initialization complete!")
    print("=" * 50)
    
    # Display database location
    database_url = os.getenv("DATABASE_URL", "sqlite:///./finco.db")
    print(f"\n📍 Database location: {database_url}")
    print("\n💡 You can now run the Streamlit app: streamlit run app.py\n")

if __name__ == "__main__":
    main()
