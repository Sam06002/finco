import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from models import Transaction, Category, Account, CategoryType
from db import get_db_session
from utils import format_currency, get_monthly_summary, get_category_totals, get_transactions_by_month

def show_reports():
    """
    Display the Reports & Analytics page with various financial visualizations
    """
    st.title("📈 Reports & Analytics")
    
    # Get user ID from session (default to 1 for demo)
    user_id = st.session_state.get('user_id', 1)
    
    # Date range selector
    st.sidebar.header("Date Range")
    
    # Default to current year
    current_year = datetime.now().year
    years = list(range(current_year - 5, current_year + 1))
    selected_year = st.sidebar.selectbox("Year", years, index=len(years)-1)
    
    # Month selection
    months = ["All"] + [datetime(2023, i, 1).strftime("%B") for i in range(1, 13)]
    selected_month = st.sidebar.selectbox("Month", months, index=0)
    
    # Convert month name to number
    month_num = None
    if selected_month != "All":
        month_num = datetime.strptime(selected_month, "%B").month
    
    # Set date range
    start_date = datetime(selected_year, 1 if month_num is None else month_num, 1)
    if month_num is None:
        end_date = datetime(selected_year, 12, 31)
    else:
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
    
    # Category breakdown
    st.subheader("Expense by Category")
    category_totals = get_category_totals(user_id, start_date, end_date, 'expense')
    
    if category_totals:
        # Create DataFrame for visualization
        df_categories = pd.DataFrame(category_totals, columns=['Category', 'Amount'])
        
        # Pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                df_categories,
                values='Amount',
                names='Category',
                title="Expense Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Bar chart
        with col2:
            fig = px.bar(
                df_categories.sort_values('Amount', ascending=False),
                x='Category',
                y='Amount',
                title="Expenses by Category",
                labels={'Amount': 'Amount (₹)'}
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expense data available for the selected period.")
    
    # Monthly trends
    st.subheader("Monthly Trends")
    
    # Get monthly data for the selected year
    with get_db_session() as db:
        monthly_data = db.query(
            extract('month', Transaction.date).label('month'),
            Category.type.label('category_type'),
            func.sum(Transaction.amount).label('total')
        ).join(
            Category, Transaction.category_id == Category.category_id
        ).filter(
            Transaction.user_id == user_id,
            extract('year', Transaction.date) == selected_year
        ).group_by(
            extract('month', Transaction.date),
            Category.type
        ).order_by(
            extract('month', Transaction.date)
        ).all()
    
    if monthly_data:
        # Prepare data for visualization
        months = []
        income = []
        expenses = []
        
        for month in range(1, 13):
            month_name = datetime(2023, month, 1).strftime('%b')
            months.append(month_name)
            
            # Get income and expenses for the month
            month_income = next((abs(m.total) for m in monthly_data 
                               if m.month == month and m.category_type == CategoryType.INCOME), 0)
            month_expenses = next((abs(m.total) for m in monthly_data 
                                 if m.month == month and m.category_type == CategoryType.EXPENSE), 0)
            
            income.append(float(month_income))
            expenses.append(float(month_expenses))
        
        # Create DataFrame
        df_monthly = pd.DataFrame({
            'Month': months,
            'Income': income,
            'Expenses': expenses,
            'Savings': [i - e for i, e in zip(income, expenses)]
        })
        
        # Line chart for income vs expenses
        fig = px.line(
            df_monthly,
            x='Month',
            y=['Income', 'Expenses', 'Savings'],
            title=f"Income vs Expenses ({selected_year})",
            labels={'value': 'Amount (₹)', 'variable': 'Type'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Bar chart for savings rate
        df_monthly['Savings Rate'] = [
            (savings / income * 100) if income > 0 else 0 
            for savings, income in zip(df_monthly['Savings'], df_monthly['Income'])
        ]
        
        fig = px.bar(
            df_monthly,
            x='Month',
            y='Savings Rate',
            title=f"Monthly Savings Rate ({selected_year})",
            labels={'Savings Rate': 'Savings Rate (%)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Account summary
    st.subheader("Account Summary")
    
    with get_db_session() as db:
        # Get account balances
        accounts = db.query(Account).filter(Account.user_id == user_id).all()
        
        if accounts:
            # Get account balances
            account_data = []
            
            for account in accounts:
                # Get total deposits and withdrawals
                deposits = db.query(
                    func.sum(Transaction.amount)
                ).filter(
                    Transaction.account_id == account.account_id,
                    Transaction.amount > 0,
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                ).scalar() or 0
                
                withdrawals = db.query(
                    func.sum(Transaction.amount)
                ).filter(
                    Transaction.account_id == account.account_id,
                    Transaction.amount < 0,
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                ).scalar() or 0
                
                account_data.append({
                    'Account': account.account_name,
                    'Type': account.type,
                    'Balance': float(account.balance),
                    'Deposits': float(deposits),
                    'Withdrawals': float(abs(withdrawals)),
                    'Net Flow': float(deposits - abs(withdrawals))
                })
            
            df_accounts = pd.DataFrame(account_data)
            
            # Display account balances
            st.write("### Account Balances")
            st.dataframe(
                df_accounts[['Account', 'Type', 'Balance']],
                column_config={
                    'Balance': st.column_config.NumberColumn(
                        'Balance',
                        format='₹%.2f'
                    )
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Account activity chart
            st.write("### Account Activity")
            fig = px.bar(
                df_accounts.melt(id_vars=['Account'], 
                               value_vars=['Deposits', 'Withdrawals'],
                               var_name='Type',
                               value_name='Amount'),
                x='Account',
                y='Amount',
                color='Type',
                barmode='group',
                title=f"Account Activity ({selected_year})",
                labels={'Amount': 'Amount (₹)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No accounts found. Please add accounts to see account summaries.")
