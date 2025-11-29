"""FinCo - Google Sheets backed personal finance tracker."""

from __future__ import annotations

import calendar
from datetime import datetime
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import json
import streamlit as st


from db import (
    add_expense_row,
    add_income_row,
    get_accounts_df,
    get_expenses_df,
    get_income_df,
    update_expense_row,
    update_income_row,
    delete_expense_row,
    delete_income_row,
)

# -----------------------------------------------------------------------------
# Page config & session
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="FinCo - Personal Finance",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",  # Auto-collapse on mobile
)

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# Mobile-friendly CSS
st.markdown("""
<style>
    /* Mobile-optimized styles */
    @media (max-width: 768px) {
        /* Reduce padding on mobile */
        .block-container {
            padding: 1rem 1rem !important;
            max-width: 100% !important;
        }
        
        /* Larger touch targets for buttons */
        .stButton button {
            min-height: 44px !important;
            font-size: 16px !important;
            padding: 0.5rem 1rem !important;
        }
        
        /* Better form input sizing */
        .stTextInput input, .stNumberInput input, .stDateInput input {
            min-height: 44px !important;
            font-size: 16px !important;
        }
        
        /* Improve data editor on mobile */
        .stDataFrame {
            font-size: 14px !important;
        }
        
        /* Stack columns on mobile */
        .row-widget.stHorizontal {
            flex-direction: column !important;
        }
        
        /* Better metrics display */
        .stMetric {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        
        /* Improve sidebar on mobile */
        .css-1d391kg {
            padding: 1rem 0.5rem !important;
        }
        
        /* Better tab spacing */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1rem !important;
            font-size: 16px !important;
        }
        
        /* Make expanders more touch-friendly */
        .streamlit-expanderHeader {
            font-size: 16px !important;
            padding: 0.75rem !important;
        }
        
        /* Better table scrolling on mobile */
        .dataframe {
            font-size: 13px !important;
        }
        
        /* Improve chart visibility */
        .js-plotly-plot {
            margin: 0 -1rem !important;
        }
    }
    
    /* General improvements for all screen sizes */
    .stButton button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Theme-aware form styling - works in both light and dark mode */
    .stForm {
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        background: transparent;
    }
    
    /* Better metric cards - theme aware */
    .stMetric {
        padding: 1rem;
        border-radius: 8px;
        background: rgba(128, 128, 128, 0.1);
    }
    
    @media (max-width: 768px) {
        .stMetric {
            margin-bottom: 0.5rem;
        }
    }
    
    /* Metric value styling */
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 600;
    }
    
    /* Cleaner headers */
    h1, h2, h3 {
        font-weight: 600;
    }
    
    /* Hide Streamlit branding on mobile for cleaner look */
    @media (max-width: 768px) {
        #MainMenu, footer, header {
            visibility: hidden;
        }
    }
    
    /* Improve input field visibility in dark mode */
    [data-baseweb="input"] {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)


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
    # Also clear all Streamlit cache to ensure immediate update
    st.cache_data.clear()


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
        st.sidebar.title("FinCo")
        st.sidebar.caption("Personal Finance Tracker")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Navigation")
    
    menu_items = [
        ("Dashboard", "dashboard"),
        ("Transactions", "transactions"),
        ("Settings", "settings"),
    ]

    for label, key in menu_items:
        active = st.session_state.page == key
        if st.sidebar.button(
            label,
            key=f"nav_{key}",
            type="primary" if active else "secondary",
            use_container_width=True,
        ):
            st.session_state.page = key
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Refresh button
    if st.sidebar.button("Refresh Data", use_container_width=True, help="Clear cache and reload data from Google Sheets"):
        refresh_cache()
        st.rerun()
    
    st.sidebar.caption(f"© {datetime.now().year} FinCo")


def expense_form(default_date: datetime | None = None, form_key: str = "expense_form"):
    with st.form(form_key):
        description = st.text_input("Description", placeholder="Groceries at BigBasket")
        category = st.text_input("Category", placeholder="Food & Dining")
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
                st.success("Expense saved successfully")
                st.rerun()


def income_form(default_date: datetime | None = None, form_key: str = "income_form"):
    with st.form(form_key):
        description = st.text_input("Income Source", placeholder="Salary")
        category = st.text_input("Category", value="Income")
        amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01, format="%.2f")
        account = st.text_input("Account", placeholder="SBI Salary")
        txn_date = st.date_input("Date", value=default_date or datetime.now())
        
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
                st.success("Income saved successfully")
                st.rerun()


# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
def format_inr(amount: float) -> str:
    if pd.isna(amount):
        return "₹0.00"

    sign = "-" if amount < 0 else ""
    amount = abs(float(amount))
    integer_part = int(amount)
    fraction_part = amount - integer_part

    last_three = str(integer_part % 1000)
    remaining = integer_part // 1000
    parts = []

    while remaining > 0:
        parts.append(f"{remaining % 100:02d}")
        remaining //= 100

    if parts:
        formatted_int = f"{','.join(reversed(parts))},{int(last_three):03d}"
    else:
        formatted_int = last_three

    formatted_fraction = f"{fraction_part:.2f}"[1:]
    return f"{sign}₹{formatted_int}{formatted_fraction}"


def show_monthly_expense_chart(expenses: pd.DataFrame) -> None:
    now = datetime.now()
    month_names = list(calendar.month_name)[1:]
    years = list(range(2023, 2027))

    default_month = now.month
    default_year = now.year

    col_month, col_year = st.columns(2)
    with col_month:
        month_name = st.selectbox(
            "Month",
            month_names,
            index=default_month - 1,
            key="monthly_expense_month",
        )
    with col_year:
        year = st.selectbox(
            "Year",
            years,
            index=years.index(default_year) if default_year in years else 0,
            key="monthly_expense_year",
        )

    month = month_names.index(month_name) + 1
    filtered = expenses.copy()

    if not filtered.empty:
        filtered["Date"] = pd.to_datetime(filtered.get("Date"), errors="coerce")
        filtered["Amount"] = pd.to_numeric(filtered.get("Amount"), errors="coerce")

        filtered = filtered.dropna(subset=["Date", "Amount"])  # type: ignore[arg-type]
        filtered = filtered.loc[
            (filtered["Date"].dt.month == month)
            & (filtered["Date"].dt.year == year)
        ]

    if filtered.empty:
        st.info(
            "No expenses recorded for this month.\nAdd an expense to see the chart update!"
        )
        return

    if "Category" not in filtered.columns:
        st.warning("Category column is missing in the Expenses sheet.")
        return

    grouped = (
        filtered.assign(Amount=filtered["Amount"].abs())
        .groupby("Category", as_index=False)["Amount"]
        .sum()
        .sort_values(by="Amount", ascending=False)
    )

    if grouped.empty:
        st.info("No expense data available for this month.")
        return

    grouped["FormattedAmount"] = grouped["Amount"].apply(format_inr)

    fig = px.bar(
        grouped,
        x="Category",
        y="Amount",
        title=f"Monthly Expenses - {month_name} {year}",
        color="Amount",
        color_continuous_scale="Blues",
        height=500,
    )

    max_amount = grouped["Amount"].max()
    tick_count = min(6, max(2, len(grouped) + 1))
    tickvals = np.linspace(0, max_amount, tick_count) if max_amount > 0 else [0]
    ticktext = [format_inr(val) for val in tickvals]

    fig.update_layout(
        margin=dict(l=40, r=20, t=60, b=40),
        coloraxis_showscale=False,
    )
    fig.update_traces(
        marker_line_width=0,
        customdata=grouped["FormattedAmount"],
        hovertemplate="Category: %{x}<br>Amount: %{customdata}<extra></extra>",
    )
    fig.update_yaxes(
        title="Amount (₹)",
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
        rangemode="tozero",
    )
    st.plotly_chart(fig, use_container_width=True)


def show_dashboard():
    st.title("Dashboard")
    expenses, income, accounts = load_sheets()

    with st.expander("Monthly Expense Insights", expanded=True):
        show_monthly_expense_chart(expenses)

    summary = calculate_monthly_summary(expenses, income)

    cols = st.columns(3)
    cols[0].metric("Income", format_inr(summary["income"]))
    cols[1].metric("Expenses", format_inr(summary["expenses"]))
    cols[2].metric(
        "Savings",
        format_inr(summary["savings"]),
        delta=f"{summary['savings_rate']:.1f}% of income",
    )

    st.markdown("---")
    st.subheader("Quick Add")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Add Expense")
        expense_form(form_key="dashboard_expense_form")
    with c2:
        st.markdown("#### Add Income")
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
    st.title("Transactions")
    expenses, income, _ = load_sheets()

    tab1, tab2 = st.tabs(["Expenses", "Income"])

    with tab1:
        st.markdown("### Expenses")
        expense_form(form_key="transactions_expense_form")
        st.markdown("---")
        if expenses.empty:
            st.info("No expenses recorded yet.")
        else:
            display_editable_transactions(expenses, is_expense=True)

    with tab2:
        st.markdown("### Income")
        income_form(form_key="transactions_income_form")
        st.markdown("---")
        if income.empty:
            st.info("No income entries recorded yet.")
        else:
            display_editable_transactions(income, is_expense=False)


def display_editable_transactions(df: pd.DataFrame, is_expense: bool):
    """Display transactions in an editable table with delete functionality."""
    
    # Prepare display dataframe
    df_display = df.copy()
    if "Date" in df_display:
        df_display = df_display.sort_values(by="Date", ascending=False)
    
    # Select and order columns
    display_columns = [
        col
        for col in ["Date", "Description", "Category", "Amount", "Account"]
        if col in df_display.columns
    ]
    df_edit = df_display[display_columns].reset_index(drop=True)
    
    # Store original indices for tracking
    original_indices = df_display.index.tolist()
    
    st.markdown("Edit transactions by clicking on any cell. Changes save automatically.")
    
    # Use data_editor for inline editing
    edited_df = st.data_editor(
        df_edit,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Date": st.column_config.DateColumn(
                "Date",
                format="YYYY-MM-DD",
                help="Transaction date"
            ),
            "Description": st.column_config.TextColumn(
                "Description",
                help="Transaction description",
                max_chars=200
            ),
            "Category": st.column_config.TextColumn(
                "Category",
                help="Transaction category",
                max_chars=100
            ),
            "Amount": st.column_config.NumberColumn(
                "Amount",
                help="Transaction amount",
                format="₹%.2f"
            ),
            "Account": st.column_config.TextColumn(
                "Account",
                help="Account name",
                max_chars=100
            ),
        },
        key=f"transaction_editor_{'expense' if is_expense else 'income'}"
    )
    
    # Auto-save: Detect changes and update instantly
    if not edited_df.equals(df_edit):
        # Find the first changed row and update it
        for idx in range(len(edited_df)):
            if idx < len(df_edit) and not edited_df.iloc[idx].equals(df_edit.iloc[idx]):
                original_idx = original_indices[idx]
                updated_data = edited_df.iloc[idx].to_dict()
                
                # Convert date to string format
                if "Date" in updated_data and pd.notna(updated_data["Date"]):
                    updated_data["Date"] = pd.to_datetime(updated_data["Date"]).strftime("%Y-%m-%d")
                
                # Update in Google Sheets
                try:
                    if is_expense:
                        update_expense_row(original_idx, updated_data)
                    else:
                        update_income_row(original_idx, updated_data)
                    
                    st.success(f"Updated: {updated_data.get('Description', 'N/A')}")
                    refresh_cache()
                    st.rerun()
                except Exception as e:
                    error_msg = str(e)
                    # Check if it's a rate limit error
                    if "429" in error_msg or "RATE_LIMIT_EXCEEDED" in error_msg:
                        st.warning("⚠️ Editing too quickly. Please wait a moment and try again.")
                    else:
                        st.error(f"Failed to update: {e}")
                # Only process one change at a time to prevent multiple reruns
                break
    
    # Delete functionality
    st.markdown("---")
    st.markdown("**Delete Transactions**")
    
    with st.expander("Delete a transaction", expanded=False):
        st.warning("This action cannot be undone.")
        
        # Create selection dropdown with transaction descriptions
        delete_options = [
            f"{idx}: {row.get('Date', 'N/A')} - {row.get('Description', 'N/A')} - {row.get('Amount', 'N/A')}"
            for idx, row in enumerate(df_edit.to_dict('records'))
        ]
        
        if delete_options:
            selected = st.selectbox(
                "Select transaction to delete:",
                options=range(len(delete_options)),
                format_func=lambda x: delete_options[x],
                key=f"delete_selector_{'expense' if is_expense else 'income'}"
            )
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Delete", type="primary", use_container_width=True):
                    original_idx = original_indices[selected]
                    try:
                        if is_expense:
                            delete_expense_row(original_idx)
                        else:
                            delete_income_row(original_idx)
                        
                        st.success("Transaction deleted successfully")
                        refresh_cache()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete: {e}")


def display_transactions(df: pd.DataFrame):
    """Fallback display for non-editable views (used in dashboard)."""
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
    st.title("Settings")
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

    st.markdown("---")
    st.subheader("Or Upload Credentials")
    st.caption("If you don't have access to secrets (e.g. on Streamlit Cloud), upload your `google-credentials.json` here.")

    uploaded_file = st.file_uploader("Upload google-credentials.json", type="json")
    if uploaded_file is not None:
        try:
            creds = json.load(uploaded_file)
            st.session_state["google_credentials"] = creds
            st.success("Credentials loaded successfully")
        except Exception as e:
            st.error(f"Invalid JSON file: {e}")
    
    if "google_credentials" in st.session_state:
        st.info("Using uploaded credentials.")
        
        current_url = st.session_state.get("spreadsheet_url", "")
        new_url = st.text_input("Spreadsheet URL", value=current_url, placeholder="https://docs.google.com/spreadsheets/d/...")
        if new_url:
            st.session_state["spreadsheet_url"] = new_url
            st.success("Spreadsheet URL saved!")



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
