"""FinCo - Google Sheets backed personal finance tracker."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Tuple

import pandas as pd
import streamlit as st

from db import (
    add_expense_row,
    add_income_row,
    get_accounts_df,
    get_expenses_df,
    get_income_df,
)

# -----------------------------------------------------------------------------
# Page config & session
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="FinCo - Google Sheets",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "page" not in st.session_state:
    st.session_state.page = "dashboard"


# -----------------------------------------------------------------------------
# Data helpers
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def _load_sheets_cached() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fetch expenses, income, and accounts worksheets."""
    expenses = get_expenses_df().copy()
    income = get_income_df().copy()
    accounts = get_accounts_df().copy()

    for frame in (expenses, income):
        if not frame.empty and "Date" in frame.columns:
            frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    return expenses, income, accounts


def load_sheets() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Safe wrapper that surfaces connection problems in the UI."""
    try:
        return _load_sheets_cached()
    except RuntimeError as exc:
        st.error(f"Google Sheets connection failed: {exc}")
        empty = pd.DataFrame()
        return empty, empty, empty


def refresh_cache() -> None:
    """Clear cached sheet data after any write."""
    _load_sheets_cached.clear()


def calculate_monthly_summary(
    expenses: pd.DataFrame, income: pd.DataFrame, target: datetime | None = None
) -> dict:
    target = target or datetime.now()
    start = target.replace(day=1)
    end = (start + pd.offsets.MonthEnd(0)).to_pydatetime()

    def _filter(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "Date" not in df:
            return pd.DataFrame(columns=df.columns)
        mask = (df["Date"] >= start) & (df["Date"] <= end)
        return df.loc[mask].copy()

    expenses_month = _filter(expenses)
    income_month = _filter(income)

    total_income = income_month.get("Amount", pd.Series(dtype=float)).sum()
    total_expenses = expenses_month.get("Amount", pd.Series(dtype=float)).sum()
    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income else 0

    return {
        "income": float(total_income),
        "expenses": float(total_expenses),
        "savings": float(savings),
        "savings_rate": float(savings_rate),
    }


def append_transaction(
    is_expense: bool,
    amount: float,
    description: str,
    category: str,
    account: str,
    txn_date: datetime,
) -> bool:
    payload = {
        "Date": txn_date.strftime("%Y-%m-%d"),
        "Description": description,
        "Amount": float(amount),
        "Category": category,
        "Account": account,
        "Created At": datetime.utcnow().isoformat(),
    }
    if is_expense:
        payload["Amount"] = -abs(payload["Amount"])
        payload["Type"] = "Expense"
        writer = add_expense_row
    else:
        payload["Amount"] = abs(payload["Amount"])
        payload["Type"] = "Income"
        writer = add_income_row

    try:
        writer(payload)
    except RuntimeError as exc:
        st.error(f"Unable to save transaction: {exc}")
        return False

    refresh_cache()
    return True


# -----------------------------------------------------------------------------
# UI Helpers
# -----------------------------------------------------------------------------
def render_sidebar() -> None:
    logo_path = Path("assets/icons/logo.png")
    if logo_path.exists():
        st.sidebar.image(str(logo_path), use_container_width=True)
    else:
        st.sidebar.title("💰 FinCo")
        st.sidebar.caption("Google Sheets Edition")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Navigation")
    
    menu_items = [
        ("Dashboard", "dashboard", "📊"),
        ("Transactions", "transactions", "💳"),
        ("Settings", "settings", "⚙️"),
    ]

    for label, key, emoji in menu_items:
        active = st.session_state.page == key
        if st.sidebar.button(
            f"{emoji} {label}",
            key=f"nav_{key}",
            type="primary" if active else "secondary",
            use_container_width=True,
        ):
            st.session_state.page = key
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"FinCo Sheets • {datetime.now().year}")


def expense_form(default_date: datetime | None = None, form_key: str = "expense_form"):
    with st.form(form_key):
        cols = st.columns(2)
        with cols[0]:
            description = st.text_input("Description", placeholder="Groceries at BigBasket")
            category = st.text_input("Category", placeholder="Food & Dining")
        with cols[1]:
            amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01, format="%.2f")
            account = st.text_input("Account", placeholder="HDFC Savings")
        txn_date = st.date_input("Date", value=default_date or datetime.now())
        submitted = st.form_submit_button(
            "Add Expense",
            type="primary",
            use_container_width=True,
            key=f"{form_key}_submit",
        )
        if submitted:
            success = append_transaction(
                is_expense=True,
                amount=amount,
                description=description,
                category=category,
                account=account,
                txn_date=datetime.combine(txn_date, datetime.min.time()),
            )
            if success:
                st.success("Expense saved to Google Sheets ✅")


def income_form(default_date: datetime | None = None, form_key: str = "income_form"):
    with st.form(form_key):
        cols = st.columns(2)
        with cols[0]:
            description = st.text_input("Income Source", placeholder="Salary")
            category = st.text_input("Category", value="Income")
        with cols[1]:
            amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01, format="%.2f")
            account = st.text_input("Account", placeholder="SBI Salary")
        txn_date = st.date_input("Date ", value=default_date or datetime.now())
        submitted = st.form_submit_button(
            "Add Income",
            type="primary",
            use_container_width=True,
            key=f"{form_key}_submit",
        )
        if submitted:
            success = append_transaction(
                is_expense=False,
                amount=amount,
                description=description,
                category=category,
                account=account,
                txn_date=datetime.combine(txn_date, datetime.min.time()),
            )
            if success:
                st.success("Income saved to Google Sheets ✅")


# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
def show_dashboard():
    st.title("📊 Dashboard")
    expenses, income, accounts = load_sheets()
    summary = calculate_monthly_summary(expenses, income)

    cols = st.columns(3)
    cols[0].metric("Income", f"₹{summary['income']:,.2f}")
    cols[1].metric("Expenses", f"₹{summary['expenses']:,.2f}")
    cols[2].metric(
        "Savings",
        f"₹{summary['savings']:,.2f}",
        delta=f"{summary['savings_rate']:.1f}% of income",
    )
    
    st.markdown("---")
    st.subheader("Quick Add")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ➖ Expense")
        expense_form(form_key="dashboard_expense_form")
    with c2:
        st.markdown("#### ➕ Income")
        income_form(form_key="dashboard_income_form")

    st.markdown("---")
    st.subheader("Recent Activity")
    merged = pd.concat(
        [expenses.assign(Type="Expense"), income.assign(Type="Income")],
        ignore_index=True,
    )
    if merged.empty:
        st.info("No transactions yet. Use the forms above to get started!")
    else:
        merged = merged.sort_values(by="Date", ascending=False).head(10)
        st.dataframe(
            merged[["Date", "Description", "Category", "Amount", "Account", "Type"]],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")
    st.subheader("Accounts Snapshot")
    if accounts.empty:
        st.info("No accounts data found in the Accounts worksheet.")
    else:
        st.dataframe(
            accounts,
            use_container_width=True,
            hide_index=True,
        )


def show_transactions():
    st.title("💳 Transactions")
    expenses, income, _ = load_sheets()

    tab1, tab2 = st.tabs(["Expenses", "Income"])

    with tab1:
        st.markdown("### Expenses")
        expense_form(form_key="transactions_expense_form")
        if expenses.empty:
            st.info("No expenses recorded yet.")
        else:
            display_transactions(expenses)

    with tab2:
        st.markdown("### Income")
        income_form(form_key="transactions_income_form")
        if income.empty:
            st.info("No income entries recorded yet.")
        else:
            display_transactions(income)


def display_transactions(df: pd.DataFrame):
    df_display = df.copy()
    if "Date" in df_display:
        df_display = df_display.sort_values(by="Date", ascending=False)
    columns = [
        col
        for col in ["Date", "Description", "Category", "Amount", "Account"]
        if col in df_display.columns
    ]
    st.dataframe(
        df_display[columns],
        use_container_width=True,
        hide_index=True,
    )


def show_settings():
    st.title("⚙️ Settings")
    st.info(
        "Update `.streamlit/secrets.toml` with your Google Sheets credentials and worksheet names."
    )
    st.code(
        """[connections.gsheets]
spreadsheet = "https://docs.google.com/..."
expenses_worksheet = "Expenses"
income_worksheet = "Income"
# Paste the remaining service account fields (type, project_id, etc.)
""",
        language="toml",
    )


# -----------------------------------------------------------------------------
# Main entry
# -----------------------------------------------------------------------------
def route(page: str) -> None:
    if page == "dashboard":
        show_dashboard()
    elif page == "transactions":
        show_transactions()
    elif page == "settings":
        show_settings()
    else:
        show_dashboard()


def main() -> None:
    render_sidebar()
    route(st.session_state.page)


if __name__ == "__main__":
    main()
