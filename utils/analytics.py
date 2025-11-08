import os
import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract, case
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from models import Transaction, Category, Account, AnalyticsCache, CategoryType

# Cache expiration time in seconds (1 hour)
CACHE_TTL = 3600

# Helper function to get date range
def get_date_range(days: int = 30) -> Tuple[date, date]:
    """Get date range for the last N days."""
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def get_cached_data(
    db: Session, 
    user_id: int, 
    cache_key: str
) -> Optional[Dict]:
    """Retrieve cached analytics data if valid."""
    cache = db.query(AnalyticsCache).filter(
        AnalyticsCache.user_id == user_id,
        AnalyticsCache.cache_key == cache_key,
        AnalyticsCache.expires_at > datetime.utcnow()
    ).first()
    
    if cache and not cache.is_expired():
        try:
            return json.loads(cache.data)
        except json.JSONDecodeError:
            return None
    return None

def set_cached_data(
    db: Session,
    user_id: int,
    cache_key: str,
    data: Any,
    ttl: int = CACHE_TTL
) -> None:
    """Store data in cache."""
    cache = db.query(AnalyticsCache).filter(
        AnalyticsCache.user_id == user_id,
        AnalyticsCache.cache_key == cache_key
    ).first()
    
    cache_data = {
        'data': data,
        'cached_at': datetime.utcnow().isoformat()
    }
    
    if cache:
        cache.data = json.dumps(cache_data)
        cache.expires_at = datetime.utcnow() + timedelta(seconds=ttl)
    else:
        cache = AnalyticsCache(
            user_id=user_id,
            cache_key=cache_key,
            data=json.dumps(cache_data),
            expires_at=datetime.utcnow() + timedelta(seconds=ttl)
        )
    
    db.add(cache)
    db.commit()

def get_spending_by_category(
    db: Session, 
    user_id: int, 
    start_date: date, 
    end_date: date,
    category_type: Optional[CategoryType] = CategoryType.EXPENSE
) -> List[Dict]:
    """Get spending by category for a given date range."""
    cache_key = f"spending_by_category_{start_date}_{end_date}_{category_type.value}"
    cached_data = get_cached_data(db, user_id, cache_key)
    if cached_data:
        return cached_data
    
    # Get all categories including those with no transactions
    categories = db.query(Category).filter(
        Category.user_id == user_id,
        Category.type == category_type
    ).all()
    
    # Get transactions for the date range
    transactions = db.query(
        Transaction.category_id,
        Category.name.label('category_name'),
        func.sum(Transaction.amount).label('total_amount')
    ).join(
        Category, Transaction.category_id == Category.category_id
    ).filter(
        Transaction.user_id == user_id,
        Transaction.date.between(start_date, end_date),
        Transaction.amount < 0,  # Only expenses
        ~Transaction.is_deleted
    ).group_by(
        Transaction.category_id,
        Category.name
    ).all()
    
    # Create a dictionary of category totals
    category_totals = {}
    for cat in categories:
        category_totals[cat.category_id] = {
            'category_id': cat.category_id,
            'category_name': cat.name,
            'amount': 0.0,
            'percentage': 0.0
        }
    
    # Update with actual transaction data
    total_spent = 0.0
    for t in transactions:
        if t.category_id in category_totals:
            amount = abs(t.total_amount or 0)
            category_totals[t.category_id]['amount'] = amount
            total_spent += amount
    
    # Calculate percentages
    for cat_id, data in category_totals.items():
        if total_spent > 0:
            data['percentage'] = (data['amount'] / total_spent) * 100
    
    # Convert to list and sort by amount
    result = sorted(
        category_totals.values(),
        key=lambda x: x['amount'],
        reverse=True
    )
    
    # Cache the result
    set_cached_data(db, user_id, cache_key, result)
    
    return result

def get_income_vs_expenses(
    db: Session, 
    user_id: int, 
    start_date: date, 
    end_date: date
) -> Dict[str, float]:
    """Get total income and expenses for a given date range."""
    cache_key = f"income_vs_expenses_{start_date}_{end_date}"
    cached_data = get_cached_data(db, user_id, cache_key)
    if cached_data:
        return cached_data
    
    # Get total expenses (negative amounts)
    expenses = db.query(
        func.coalesce(func.sum(Transaction.amount), 0.0)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.amount < 0,
        Transaction.date.between(start_date, end_date),
        ~Transaction.is_deleted
    ).scalar() or 0.0
    
    # Get total income (positive amounts)
    income = db.query(
        func.coalesce(func.sum(Transaction.amount), 0.0)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.amount > 0,
        Transaction.date.between(start_date, end_date),
        ~Transaction.is_deleted
    ).scalar() or 0.0
    
    result = {
        'income': float(income),
        'expenses': float(abs(expenses)),
        'savings': float(income + expenses)  # expenses is negative
    }
    
    # Cache the result
    set_cached_data(db, user_id, cache_key, result)
    
    return result

def get_spending_trends(
    db: Session, 
    user_id: int, 
    start_date: date, 
    end_date: date,
    group_by: str = 'month'  # 'day', 'week', 'month', 'year'
) -> List[Dict]:
    """Get spending trends over time."""
    cache_key = f"spending_trends_{start_date}_{end_date}_{group_by}"
    cached_data = get_cached_data(db, user_id, cache_key)
    if cached_data:
        return cached_data
    
    # Determine the date part to group by
    if group_by == 'day':
        date_format = '%Y-%m-%d'
        date_trunc = func.date(Transaction.date)
    elif group_by == 'week':
        date_format = '%Y-W%U'
        date_trunc = func.strftime('%Y-W%W', Transaction.date)
    elif group_by == 'month':
        date_format = '%Y-%m'
        date_trunc = func.strftime('%Y-%m', Transaction.date)
    else:  # year
        date_format = '%Y'
        date_trunc = func.strftime('%Y', Transaction.date)
    
    # Query for expenses
    expenses = db.query(
        date_trunc.label('period'),
        func.sum(Transaction.amount).label('amount')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.amount < 0,
        Transaction.date.between(start_date, end_date),
        ~Transaction.is_deleted
    ).group_by(
        'period'
    ).order_by(
        'period'
    ).all()
    
    # Query for income
    income = db.query(
        date_trunc.label('period'),
        func.sum(Transaction.amount).label('amount')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.amount > 0,
        Transaction.date.between(start_date, end_date),
        ~Transaction.is_deleted
    ).group_by(
        'period'
    ).order_by(
        'period'
    ).all()
    
    # Convert to dictionaries for easier processing
    expense_dict = {e.period: abs(e.amount) for e in expenses}
    income_dict = {i.period: i.amount for i in income}
    
    # Get all unique periods
    all_periods = sorted(set(list(expense_dict.keys()) + list(income_dict.keys())))
    
    # Build result
    result = []
    for period in all_periods:
        result.append({
            'period': period,
            'expenses': float(expense_dict.get(period, 0.0)),
            'income': float(income_dict.get(period, 0.0)),
            'savings': float(income_dict.get(period, 0.0) - expense_dict.get(period, 0.0))
        })
    
    # Cache the result
    set_cached_data(db, user_id, cache_key, result)
    
    return result

def get_account_balances(db: Session, user_id: int) -> List[Dict]:
    """Get current balances for all accounts."""
    cache_key = f"account_balances_{user_id}"
    cached_data = get_cached_data(db, user_id, cache_key)
    if cached_data:
        return cached_data
    
    # Get all accounts with their current balance
    accounts = db.query(
        Account
    ).filter(
        Account.user_id == user_id,
        ~Account.is_deleted
    ).all()
    
    # Calculate total balance
    total_balance = sum(account.balance for account in accounts)
    
    # Prepare result
    result = []
    for account in accounts:
        percentage = (account.balance / total_balance * 100) if total_balance != 0 else 0
        result.append({
            'account_id': account.account_id,
            'name': account.name,
            'balance': float(account.balance),
            'currency': account.currency,
            'percentage': float(percentage)
        })
    
    # Sort by balance (highest first)
    result.sort(key=lambda x: x['balance'], reverse=True)
    
    # Cache the result (with a shorter TTL since account balances change frequently)
    set_cached_data(db, user_id, cache_key, result, ttl=600)  # 10 minutes
    
    return result

def get_financial_health_score(
    db: Session, 
    user_id: int, 
    months: int = 12
) -> Dict[str, Any]:
    """Calculate a financial health score (0-100)."""
    end_date = datetime.utcnow().date()
    start_date = (end_date - relativedelta(months=months)).replace(day=1)
    
    cache_key = f"financial_health_{start_date}_{end_date}"
    cached_data = get_cached_data(db, user_id, cache_key)
    if cached_data:
        return cached_data
    
    # Get income and expenses
    income_expenses = get_income_vs_expenses(db, user_id, start_date, end_date)
    
    # Calculate savings rate (savings / income)
    if income_expenses['income'] > 0:
        savings_rate = (income_expenses['savings'] / income_expenses['income']) * 100
    else:
        savings_rate = 0.0
    
    # Get account balances
    accounts = get_account_balances(db, user_id)
    total_balance = sum(acc['balance'] for acc in accounts)
    
    # Calculate emergency fund (months of expenses covered)
    avg_monthly_expenses = abs(income_expenses['expenses']) / months
    emergency_fund_months = (total_balance / avg_monthly_expenses) if avg_monthly_expenses > 0 else 0
    
    # Calculate debt-to-income ratio
    debt = sum(acc['balance'] for acc in accounts if acc['balance'] < 0)
    debt_to_income = (abs(debt) / income_expenses['income']) if income_expenses['income'] > 0 else 0
    
    # Calculate score components (0-100 each)
    savings_score = min(savings_rate * 2, 100)  # 50% savings rate = 100 points
    emergency_score = min(emergency_fund_months * 10, 100)  # 10 months = 100 points
    debt_score = max(0, 100 - (debt_to_income * 100))  # 0% = 100, 100% = 0
    
    # Calculate overall score (weighted average)
    overall_score = int((savings_score * 0.4) + (emergency_score * 0.3) + (debt_score * 0.3))
    
    result = {
        'score': overall_score,
        'savings_rate': savings_rate,
        'emergency_fund_months': emergency_fund_months,
        'debt_to_income': debt_to_income,
        'total_balance': total_balance,
        'avg_monthly_income': income_expenses['income'] / months,
        'avg_monthly_expenses': avg_monthly_expenses,
        'last_updated': datetime.utcnow().isoformat()
    }
    
    # Cache the result
    set_cached_data(db, user_id, cache_key, result)
    
    return result

def create_spending_by_category_plot(data: List[Dict], title: str = "Spending by Category") -> go.Figure:
    """Create a donut chart for spending by category."""
    if not data:
        return None
        
    df = pd.DataFrame(data)
    
    # Filter out categories with 0 amount
    df = df[df['amount'] > 0]
    
    if df.empty:
        return None
    
    # Create the figure
    fig = px.pie(
        df,
        values='amount',
        names='category_name',
        title=title,
        hole=0.5,
        hover_data=['amount'],
        labels={'amount': 'Amount', 'category_name': 'Category'}
    )
    
    # Update layout
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}<br>%{value:$,.2f} (%{percent})<extra></extra>'
    )
    
    fig.update_layout(
        margin=dict(t=40, b=10, l=10, r=10),
        showlegend=False,
        height=400
    )
    
    return fig

def create_income_vs_expenses_plot(data: Dict, title: str = "Income vs Expenses") -> go.Figure:
    """Create a bar chart for income vs expenses."""
    if not data:
        return None
    
    # Prepare data for plotting
    categories = ['Income', 'Expenses', 'Savings']
    values = [data.get('income', 0), data.get('expenses', 0), data.get('savings', 0)]
    
    # Create the figure
    fig = go.Figure()
    
    # Add bars
    colors = ['#2ecc71', '#e74c3c', '#3498db']
    for i, (cat, val, color) in enumerate(zip(categories, values, colors)):
        fig.add_trace(go.Bar(
            x=[cat],
            y=[val],
            name=cat,
            marker_color=color,
            text=[f"${val:,.2f}"],
            textposition='auto',
            hovertemplate=f"{cat}: ${val:,.2f}<extra></extra>"
        ))
    
    # Update layout
    fig.update_layout(
        title=title,
        showlegend=False,
        margin=dict(t=40, b=10, l=10, r=10),
        height=400,
        yaxis=dict(title='Amount ($)')
    )
    
    return fig

def create_spending_trends_plot(data: List[Dict], title: str = "Spending Trends") -> go.Figure:
    """Create a line chart for spending trends over time."""
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    # Create the figure
    fig = go.Figure()
    
    # Add traces for income, expenses, and savings
    fig.add_trace(go.Scatter(
        x=df['period'],
        y=df['income'],
        name='Income',
        mode='lines+markers',
        line=dict(color='#2ecc71', width=3),
        hovertemplate='%{x}<br>Income: $%{y:,.2f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['period'],
        y=df['expenses'],
        name='Expenses',
        mode='lines+markers',
        line=dict(color='#e74c3c', width=3),
        hovertemplate='%{x}<br>Expenses: $%{y:,.2f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['period'],
        y=df['savings'],
        name='Savings',
        mode='lines+markers',
        line=dict(color='#3498db', width=3, dash='dash'),
        hovertemplate='%{x}<br>Savings: $%{y:,.2f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Period',
        yaxis_title='Amount ($)',
        margin=dict(t=40, b=40, l=40, r=40),
        height=400,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig
