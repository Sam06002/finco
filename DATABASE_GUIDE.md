# FinCo Database Guide

## Quick Start

### 1. Initialize Database
```bash
python init_database.py
```

This creates all tables and optionally adds sample data.

## Database Configuration

The database connection is configured in `.env`:

```env
DATABASE_URL=sqlite:///./finco.db
```

### Supported Databases

- **SQLite** (default): `sqlite:///./finco.db`
- **PostgreSQL**: `postgresql://username:password@localhost/finco`
- **MySQL**: `mysql://username:password@localhost/finco`

## Database Models

### User
- Primary fields: `user_id`, `username`, `email`, `hashed_password`
- Relationships: All other entities

### Account
- Primary fields: `account_id`, `account_name`, `type`, `institution`, `balance`
- Belongs to: `User`
- Has many: `Transaction`

### Category
- Primary fields: `category_id`, `name`, `type` (expense/income/investment)
- Belongs to: `User`
- Has many: `Transaction`, `Budget`

### Transaction
- Primary fields: `transaction_id`, `date`, `merchant`, `amount`
- Belongs to: `User`, `Account`, `Category`
- Many-to-many: `Tag`

### Budget
- Primary fields: `budget_id`, `amount`, `period` (monthly/yearly)
- Belongs to: `User`, `Category`

### Goal
- Primary fields: `goal_id`, `name`, `target_amount`, `current_amount`, `status`
- Belongs to: `User`

### Tag
- Primary fields: `tag_id`, `label`
- Belongs to: `User`
- Many-to-many: `Transaction`

### Investment
- Primary fields: `investment_id`, `name`, `type`, `amount`, `current_value`
- Belongs to: `User`

### NetWorthSnapshot
- Primary fields: `snapshot_id`, `date`, `total_assets`, `total_liabilities`
- Computed property: `net_worth`
- Belongs to: `User`

## Working with the Database

### Method 1: Context Manager (Recommended)

```python
from db import DatabaseSession
from models import User

# Automatically handles commit/rollback
with DatabaseSession() as db:
    user = User(
        username="john_doe",
        email="john@example.com",
        hashed_password="hashed_password_here"
    )
    db.add(user)
    # Automatically commits when exiting context
```

### Method 2: Direct Session

```python
from db import get_db_session
from models import User

db = get_db_session()
try:
    user = db.query(User).filter_by(username="john_doe").first()
    print(user)
finally:
    db.close()
```

### Method 3: Generator Pattern

```python
from db import get_db
from models import User

for db in get_db():
    users = db.query(User).all()
    print(users)
```

## Common Operations

### Create a User
```python
from db import DatabaseSession
from models import User

with DatabaseSession() as db:
    user = User(
        username="alice",
        email="alice@example.com",
        hashed_password="$2b$12$..."
    )
    db.add(user)
```

### Create an Account
```python
from db import DatabaseSession
from models import Account

with DatabaseSession() as db:
    account = Account(
        user_id=1,
        account_name="Main Checking",
        type="checking",
        institution="Chase Bank",
        balance=5000.00
    )
    db.add(account)
```

### Create a Transaction with Tags
```python
from db import DatabaseSession
from models import Transaction, Tag
from datetime import datetime

with DatabaseSession() as db:
    # Get or create tags
    essential_tag = db.query(Tag).filter_by(label="essential").first()
    recurring_tag = db.query(Tag).filter_by(label="recurring").first()
    
    # Create transaction
    transaction = Transaction(
        user_id=1,
        account_id=1,
        date=datetime.now(),
        merchant="Electric Company",
        description="Monthly bill",
        amount=-85.50,
        category_id=1,
        is_manual=False,
        is_investment=False
    )
    
    # Add tags
    transaction.tags.append(essential_tag)
    transaction.tags.append(recurring_tag)
    
    db.add(transaction)
```

### Query Examples

```python
from db import get_db_session
from models import User, Transaction, Account
from datetime import datetime, timedelta

db = get_db_session()

# Get user by username
user = db.query(User).filter_by(username="alice").first()

# Get all transactions for a user
transactions = db.query(Transaction).filter_by(user_id=user.user_id).all()

# Get transactions in date range
start_date = datetime.now() - timedelta(days=30)
recent_transactions = db.query(Transaction).filter(
    Transaction.user_id == user.user_id,
    Transaction.date >= start_date
).order_by(Transaction.date.desc()).all()

# Get total balance across all accounts
from sqlalchemy import func
total_balance = db.query(func.sum(Account.balance)).filter_by(user_id=user.user_id).scalar()

# Get transactions with specific tags
tagged_transactions = db.query(Transaction).join(Transaction.tags).filter(
    Tag.label == "essential"
).all()

db.close()
```

### Update Operations

```python
from db import DatabaseSession
from models import Account

with DatabaseSession() as db:
    account = db.query(Account).filter_by(account_id=1).first()
    account.balance += 500.00  # Deposit
    # Automatically commits when exiting
```

### Delete Operations

```python
from db import DatabaseSession
from models import Transaction

with DatabaseSession() as db:
    transaction = db.query(Transaction).filter_by(transaction_id=123).first()
    if transaction:
        db.delete(transaction)
    # Automatically commits when exiting
```

## Migration Tips

If you modify the models:

1. **For development**: Delete the database and reinitialize
   ```bash
   rm finco.db
   python init_database.py
   ```

2. **For production**: Use Alembic for migrations
   ```bash
   pip install alembic
   alembic init alembic
   alembic revision --autogenerate -m "Description of changes"
   alembic upgrade head
   ```

## Troubleshooting

### Database locked error (SQLite)
- Ensure you're closing sessions properly
- Use context managers to automatically handle session lifecycle

### Foreign key constraint errors
- Ensure referenced records exist before creating relationships
- Check cascade settings for delete operations

### Import errors
- Ensure all models are imported in `db.py` before calling `Base.metadata.create_all()`
- Check circular import issues

## Best Practices

1. **Always use context managers** for automatic commit/rollback
2. **Close sessions** when using direct session method
3. **Use transactions** for multiple related operations
4. **Index frequently queried fields** (already done in models)
5. **Validate data** before database operations
6. **Use eager loading** (joinedload) for relationships when needed
7. **Handle exceptions** gracefully

## Performance Tips

```python
from sqlalchemy.orm import joinedload

# Eager load relationships to avoid N+1 queries
transactions = db.query(Transaction).options(
    joinedload(Transaction.account),
    joinedload(Transaction.category),
    joinedload(Transaction.tags)
).all()
```
