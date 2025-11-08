"""
FinCo - Simple Expense Tracker
A minimal expense tracking application.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple, Dict

# Import local modules
from models import Transaction, Category, CategoryType
from db import init_db, get_db_session

# Initialize database
init_db()

# Set page config
st.set_page_config(
    page_title="FinCo - Expense Tracker",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def render_sidebar():
    """
    Render the sidebar navigation menu.
    
    This function creates the left sidebar with:
    - Application logo (if available)
    - Navigation menu items
    - Version information
    """
    
    # -----------------------------------------------------------------------
    # Logo Section
    # -----------------------------------------------------------------------
    # Try to load and display logo from assets/icons/ directory
    logo_path = Path("assets/icons/logo.png")
    
    if logo_path.exists():
        st.sidebar.image(str(logo_path), use_container_width=True)
    else:
        # Display app title with emoji if no logo is found
        st.sidebar.title("💰 FinCo")
        st.sidebar.caption("Personal Finance Tracker")
    
    st.sidebar.markdown("---")
    
    # -----------------------------------------------------------------------
    # Navigation Menu
    # -----------------------------------------------------------------------
    # Define menu items for sidebar navigation
    # Each tuple contains: (display_name, internal_key, emoji_icon)
    menu_items = [
        ("Dashboard", "dashboard", "📊"),
        ("Transactions", "transactions", "💳"),
        ("Budgets", "budgets", "💰"),
        ("Goals", "goals", "🎯"),
        ("Investments", "investments", "📈"),
        ("Reports", "reports", "📊"),
        ("Import", "import", "📥"),
        ("Settings", "settings", "⚙️")
    ]
    
    # Render menu items
    st.sidebar.markdown("### Navigation")
    
    # Default to dashboard if no page is set
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'
    
    # Create buttons for each menu item
    for item in menu_items:
        display_name, page_key, emoji = item
        if st.sidebar.button(f"{emoji} {display_name}", 
                           key=f"menu_{page_key}",
                           use_container_width=True,
                           type="primary" if st.session_state.page == page_key else "secondary"):
            st.session_state.page = page_key
            st.rerun()
    
    # Add some space before the version info
    st.sidebar.markdown("---")
    st.sidebar.caption(f"FinCo v1.0.0\n© {datetime.now().year} FinCo")
    
    # Add a logout button at the bottom
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        # Clear session state and redirect to login
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # -----------------------------------------------------------------------
    # Footer Section
    # -----------------------------------------------------------------------
    # Display version info and help text at the bottom of sidebar
    st.sidebar.info(
        "**FinCo v1.0.0**\n\n"
        "Your personal finance companion"
    )
    
    # Optional: Add quick stats or user info here in the future
    # Example:
    # if st.session_state.authenticated:
    #     st.sidebar.success(f"Logged in as: {st.session_state.username}")

# ============================================================================
# PAGE FUNCTIONS
# ============================================================================
# Each function below renders a specific page of the application.
# Expand these functions to add actual functionality as development progresses.

def show_dashboard():
    """
    Dashboard Page - Landing page with financial overview.
    Displays key metrics, recent transactions, and quick actions.
    """
    st.title("📊 Dashboard")
    
    # Get user ID from session (default to 1 for demo)
    user_id = st.session_state.get('user_id', 1)
    
    # Get current month summary
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get monthly summary
    summary = get_monthly_summary(user_id, current_year, current_month)
    
    # Top section with metrics
    st.markdown("### Monthly Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Income",
            value=f"₹{summary['income']:,.2f}",
            help="Total income for the current month"
        )
    
    with col2:
        st.metric(
            label="Expenses",
            value=f"₹{summary['expenses']:,.2f}",
            delta=f"-₹{summary['expenses']:,.2f} spent",
            delta_color="inverse",
            help="Total expenses for the current month"
        )
    
    with col3:
        st.metric(
            label="Savings",
            value=f"₹{summary['savings']:,.2f}",
            delta=f"{summary['savings_rate']:.1f}% of income",
            delta_color="normal" if summary['savings'] >= 0 else "inverse",
            help="Savings for the current month"
        )
    
    st.markdown("---")
    
    # Quick add expense form
    with st.expander("➕ Add Quick Expense", expanded=False):
        with st.form("quick_expense_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                amount = st.number_input(
                    "Amount (₹)", 
                    min_value=0.01, 
                    step=0.01, 
                    format="%.2f"
                )
                date = st.date_input("Date", value=datetime.now())
            
            with col2:
                categories = ["Food", "Transportation", "Shopping", "Bills", "Entertainment", "Other"]
                category = st.selectbox("Category", options=categories)
                
                accounts = ["Cash", "Bank Account", "Credit Card"]  # Replace with actual accounts
                account = st.selectbox("Account", options=accounts)
            
            description = st.text_input("Description")
            
            submitted = st.form_submit_button("Add Expense")
            
            if submitted:
                # TODO: Implement transaction creation
                st.success(f"Added expense of ₹{amount:,.2f} for {description}")
                st.experimental_rerun()
    
    # Recent transactions
    st.markdown("### Recent Transactions")
    
    # Get recent transactions
    transactions = get_transactions_by_month(user_id, current_year, current_month, 'expense')
    
    if transactions:
        # Convert to DataFrame for display
        df_transactions = pd.DataFrame(transactions)
        
        # Format date and amount
        df_transactions['date'] = pd.to_datetime(df_transactions['date']).dt.strftime('%b %d')
        
        # Display as a table
        st.dataframe(
            df_transactions[['date', 'description', 'category', 'amount']],
            column_config={
                'date': 'Date',
                'description': 'Description',
                'category': 'Category',
                'amount': st.column_config.NumberColumn(
                    'Amount',
                    format='₹%.2f'
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Show total for the month
        total_expenses = sum(t['amount'] for t in transactions)
        st.markdown(f"**Total for {datetime.now().strftime('%B %Y')}: ₹{total_expenses:,.2f}**")
    else:
        st.info("No transactions found for this month. Add your first expense using the form above!")
    
    # Upcoming bills (placeholder)
    st.markdown("---")
    st.markdown("### Upcoming Bills")
    st.info("No upcoming bills in the next 7 days.")

def show_transactions():
    """
    Transactions Page - View and manage all financial transactions.
    
    TODO: Implement the following features:
    - Add new transaction form (manual entry)
    - Transaction list with filters (date, category, account, type)
    - Edit/delete transaction capability
    - Transaction search functionality
    - Export transactions to CSV
    - Bulk operations (categorize multiple, delete multiple)
    - Transaction tags and notes
    """
    
    st.title("💸 Transactions")
    st.header("Transactions – Coming Soon!")
    
    st.info(
        "This section will allow you to:\n\n"
        "✅ **Add transactions** manually or via import\n"
        "✅ **View all transactions** with advanced filtering\n"
        "✅ **Edit and delete** transactions\n"
        "✅ **Search** by description, merchant, or amount\n"
        "✅ **Tag transactions** for better organization\n"
        "✅ **Export** transaction history to CSV"
    )
    
    # Placeholder for future functionality
    with st.expander("🎯 Planned Features", expanded=False):
        st.markdown("""
        - Multi-currency support
        - Recurring transaction templates
        - Transaction splits (multiple categories)
        - Attachments (receipts, invoices)
        - Bulk edit capabilities
        - Advanced analytics
        """)

def show_budgets():
    """
    Budgets Page - Create and track spending budgets.
    
    TODO: Implement the following features:
    - Create budget by category and time period
    - Track budget vs actual spending
    - Visual progress bars
    - Budget alerts when approaching/exceeding limits
    - Budget templates (monthly, yearly)
    - Budget comparison across periods
    - Rollover unused budget amounts
    """
    
    st.title("🎯 Budgets")
    st.header("Budgets – Coming Soon!")
    
    st.info(
        "This section will allow you to:\n\n"
        "✅ **Create budgets** for different categories and time periods\n"
        "✅ **Track spending** against budget limits\n"
        "✅ **Set alerts** for budget thresholds\n"
        "✅ **Visualize progress** with charts and indicators\n"
        "✅ **Compare periods** to identify trends\n"
        "✅ **Export reports** for analysis"
    )

def show_goals():
    """
    Goals Page - Set and track financial goals.
    
    TODO: Implement the following features:
    - Create savings goals with target amounts and deadlines
    - Track progress towards goals
    - Link goals to specific accounts
    - Goal milestones and achievements
    - Goal priority management
    - Projected completion date based on savings rate
    - Goal templates (emergency fund, vacation, etc.)
    """
    
    st.title("🏆 Goals")
    st.header("Goals – Coming Soon!")
    
    st.info(
        "This section will allow you to:\n\n"
        "✅ **Set financial goals** with target amounts and deadlines\n"
        "✅ **Track progress** visually with progress bars\n"
        "✅ **Link goals** to specific savings accounts\n"
        "✅ **Set milestones** and celebrate achievements\n"
        "✅ **Project completion** based on current savings rate\n"
        "✅ **Prioritize goals** and adjust strategies"
    )

def show_investments():
    """
    Investments Page - Track investment portfolios and performance.
    
    TODO: Implement the following features:
    - Add investment holdings (stocks, bonds, mutual funds, etc.)
    - Track portfolio performance
    - View returns and gains/losses
    - Asset allocation visualization
    - Dividend tracking
    - Investment transactions history
    - Portfolio rebalancing suggestions
    """
    
    st.title("📈 Investments")
    st.header("Investments – Coming Soon!")
    
    st.info(
        "This section will allow you to:\n\n"
        "✅ **Track investments** across multiple asset types\n"
        "✅ **Monitor performance** with real-time data\n"
        "✅ **Calculate returns** and gains/losses\n"
        "✅ **Visualize allocation** across asset classes\n"
        "✅ **Track dividends** and income\n"
        "✅ **Analyze portfolio** health and diversity"
    )

def show_import():
    """
    Import Statement Page - Import transactions from bank statements.
    
    Features:
    - Upload CSV, Excel, or PDF files
    - Preview imported data
    - Validate required columns
    - Process and clean transactions
    """
    
    st.title("📄 Import Bank Statement")
    st.markdown("Upload your bank statement to automatically import transactions.")
    
    # -----------------------------------------------------------------------
    # Instructions Section
    # -----------------------------------------------------------------------
    with st.expander("📖 Instructions", expanded=False):
        st.markdown("""
        ### Supported File Formats
        - **CSV** (.csv) - Comma-separated values
        - **Excel** (.xlsx, .xls) - Excel spreadsheets
        - **PDF** (.pdf) - Bank statement PDFs (table extraction)
        
        ### Required Columns
        Your file must contain at least these columns (case-insensitive):
        - **Date** - Transaction date
        - **Description** - Transaction description/merchant
        - **Amount** - Transaction amount (positive for credit, negative for debit)
        
        ### Optional Columns
        - Category, Account, Type, Balance, Reference, Notes
        
        ### Tips for Best Results
        1. **CSV/Excel**: Ensure first row contains column headers
        2. **PDF**: Works best with tabular bank statements
        3. **Dates**: Use standard formats (DD/MM/YYYY, YYYY-MM-DD)
        4. **Amounts**: Numbers only (₹ symbols will be removed automatically)
        """)
    
    st.markdown("---")
    
    # -----------------------------------------------------------------------
    # File Upload Section
    # -----------------------------------------------------------------------
    st.subheader("📤 Upload Statement File")
    
    uploaded_file = st.file_uploader(
        "Choose a file to import",
        type=["csv", "xlsx", "xls", "pdf"],
        help="Upload your bank statement (CSV, Excel, or PDF format)",
        key="statement_uploader"
    )
    
    # -----------------------------------------------------------------------
    # File Processing Section
    # -----------------------------------------------------------------------
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            file_size_kb = uploaded_file.size / 1024
            st.metric("File Size", f"{file_size_kb:.2f} KB")
        with col3:
            file_ext = utils.get_file_extension(uploaded_file.name)
            st.metric("File Type", file_ext.upper())
        
        st.markdown("---")
        
        # Process file based on type
        df = None
        error_message = None
        pdf_text = None
        
        with st.spinner("Processing file..."):
            if file_ext == 'csv':
                # -------------------------------------------------------
                # CSV File Processing
                # -------------------------------------------------------
                df, error_message = utils.read_csv_file(uploaded_file)
                
            elif file_ext in ['xlsx', 'xls']:
                # -------------------------------------------------------
                # Excel File Processing
                # -------------------------------------------------------
                df, error_message = utils.read_excel_file(uploaded_file)
                
            elif file_ext == 'pdf':
                # -------------------------------------------------------
                # PDF File Processing
                # -------------------------------------------------------
                df, pdf_text, error_message = utils.read_pdf_file(uploaded_file)
        
        # -----------------------------------------------------------------------
        # Display Results
        # -----------------------------------------------------------------------
        if error_message:
            # Show error message
            st.error(f"❌ {error_message}")
            st.warning("Please check your file format and try again.")
            
        else:
            st.success("✅ File processed successfully!")
            
            # -------------------------------------------------------
            # For PDF: Show extracted text/tables
            # -------------------------------------------------------
            if file_ext == 'pdf':
                st.subheader("📄 PDF Content Preview")
                
                if df is not None:
                    st.info("✅ Table found in PDF and extracted successfully!")
                elif pdf_text:
                    st.warning("⚠️ No tables found. Showing text content from first page:")
                    with st.expander("View PDF Text", expanded=True):
                        st.text(pdf_text[:2000] + "..." if len(pdf_text) > 2000 else pdf_text)
                    st.info("💡 **Tip**: For best results, use bank statements with clear table formatting.")
            
            # -------------------------------------------------------
            # Display DataFrame if available
            # -------------------------------------------------------
            if df is not None:
                st.subheader("📊 Data Preview")
                
                # Show basic stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", len(df))
                with col2:
                    st.metric("Total Columns", len(df.columns))
                with col3:
                    # Check for null values
                    null_count = df.isnull().sum().sum()
                    st.metric("Missing Values", null_count)
                
                # Display first 10 rows
                st.markdown("##### First 10 Rows")
                st.dataframe(
                    df.head(10),
                    use_container_width=True,
                    height=400
                )
                
                # Show column information
                with st.expander("📋 Column Information", expanded=False):
                    col_info = pd.DataFrame({
                        'Column Name': df.columns,
                        'Data Type': df.dtypes.values,
                        'Non-Null Count': df.count().values,
                        'Null Count': df.isnull().sum().values
                    })
                    st.dataframe(col_info, use_container_width=True)
                
                st.markdown("---")
                
                # -------------------------------------------------------
                # Column Mapping Section
                # -------------------------------------------------------
                st.subheader("🔗 Column Mapping")
                
                st.info("""
                **Map your file columns to standard fields:**
                
                - **Date**: Transaction date (required)
                - **Description**: Transaction details/merchant (required)  
                - **Amount**: Transaction amount (required)
                - **Merchant**: Merchant name (optional)
                - **Account**: Account name/number (optional)
                - **Category**: Transaction category (optional)
                """)
                
                # Auto-detect column mappings
                auto_mappings = auto_detect_column_mapping(df.columns)
                
                # Column mapping form
                with st.form("column_mapping_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Required fields
                        st.markdown("**Required Fields**")
                        date_col = st.selectbox(
                            "Date Column",
                            options=[""] + list(df.columns),
                            index=auto_mappings.get('date', 0),
                            help="Transaction date (required)"
                        )
                        
                        desc_col = st.selectbox(
                            "Description Column", 
                            options=[""] + list(df.columns),
                            index=auto_mappings.get('description', 0),
                            help="Transaction description/merchant (required)"
                        )
                        
                        amount_col = st.selectbox(
                            "Amount Column",
                            options=[""] + list(df.columns),
                            index=auto_mappings.get('amount', 0),
                            help="Transaction amount (required)"
                        )
                    
                    with col2:
                        # Optional fields
                        st.markdown("**Optional Fields**")
                        merchant_col = st.selectbox(
                            "Merchant Column",
                            options=[""] + list(df.columns),
                            index=auto_mappings.get('merchant', 0),
                            help="Merchant name (optional)"
                        )
                        
                        account_col = st.selectbox(
                            "Account Column",
                            options=[""] + list(df.columns),
                            index=auto_mappings.get('account', 0),
                            help="Account name/number (optional)"
                        )
                        
                        category_col = st.selectbox(
                            "Category Column",
                            options=[""] + list(df.columns),
                            index=auto_mappings.get('category', 0),
                            help="Transaction category (optional)"
                        )
                    
                    # Submit button
                    submitted = st.form_submit_button("✅ Confirm Mapping & Parse Data", type="primary", use_container_width=True)
                
                # Handle form submission
                if submitted:
                    # Validate required fields are mapped
                    if not date_col or not desc_col or not amount_col:
                        st.error("❌ Please map all required fields (Date, Description, Amount)")
                    else:
                        # Parse and standardize data
                        with st.spinner("Parsing and standardizing data..."):
                            df_parsed = parse_and_standardize_dataframe(
                                df, date_col, desc_col, amount_col, 
                                merchant_col, account_col, category_col
                            )
                            
                            # Store in session state
                            st.session_state['parsed_data'] = df_parsed
                            st.session_state['import_file_name'] = uploaded_file.name
                            st.session_state['column_mapping'] = {
                                'date': date_col,
                                'description': desc_col,
                                'amount': amount_col,
                                'merchant': merchant_col,
                                'account': account_col,
                                'category': category_col
                            }
                            
                            st.success("✅ Data parsed and standardized successfully!")
                            
                            # Show parsed data preview
                            st.markdown("---")
                            st.subheader("📋 Parsed Transaction Preview")
                            
                            # Show summary stats
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Total Transactions", len(df_parsed))
                            with col2:
                                income_count = len(df_parsed[df_parsed['amount'] > 0])
                                st.metric("Income Transactions", income_count)
                            with col3:
                                expense_count = len(df_parsed[df_parsed['amount'] < 0])
                                st.metric("Expense Transactions", expense_count)
                            with col4:
                                total_income = df_parsed[df_parsed['amount'] > 0]['amount'].sum()
                                st.metric("Total Income", f"₹{total_income:,.2f}")
                            
                            # Initialize edit state if not exists
                            if 'transaction_edits' not in st.session_state:
                                st.session_state.transaction_edits = {}
                            
                            if 'new_categories' not in st.session_state:
                                st.session_state.new_categories = set()
                            
                            # Show editable transaction preview
                            st.markdown("##### Edit Transactions Before Import")
                            
                            # Get existing categories for dropdown
                            existing_categories = get_existing_categories()
                            
                            # Create editable interface
                            edited_count = 0
                            for idx, (_, row) in enumerate(df_parsed.iterrows()):
                                # Check if this transaction has edits
                                edit_key = f"txn_{idx}"
                                has_edits = edit_key in st.session_state.transaction_edits
                                
                                if has_edits:
                                    edited_count += 1
                                
                                # Create container for each transaction
                                with st.container():
                                    col1, col2, col3 = st.columns([0.5, 0.3, 0.2])
                                    
                                    with col1:
                                        # Transaction details
                                        st.markdown(f"**Transaction {idx + 1}**")
                                        if has_edits:
                                            st.markdown("🔧 *Edited*")
                                        
                                        # Display original values
                                        st.caption(f"Original: {row['description'][:30]}...")
                                    
                                    with col2:
                                        # Edit form
                                        with st.form(f"edit_form_{idx}"):
                                            # Merchant rename
                                            current_merchant = st.session_state.transaction_edits.get(edit_key, {}).get('merchant', row.get('merchant', ''))
                                            merchant_input = st.text_input(
                                                "Merchant Name",
                                                value=current_merchant or row.get('merchant', ''),
                                                key=f"merchant_{idx}",
                                                placeholder="Enter merchant name"
                                            )
                                            
                                            # Category dropdown
                                            current_category = st.session_state.transaction_edits.get(edit_key, {}).get('category', row.get('category', ''))
                                            category_options = [""] + list(existing_categories) + ["➕ Create New Category"]
                                            category_idx = 0
                                            if current_category:
                                                if current_category in existing_categories:
                                                    category_idx = existing_categories.index(current_category) + 1
                                                else:
                                                    category_idx = len(existing_categories) + 1
                                            
                                            selected_category = st.selectbox(
                                                "Category",
                                                options=category_options,
                                                index=category_idx,
                                                key=f"category_{idx}"
                                            )
                                            
                                            # Date input
                                            current_date = st.session_state.transaction_edits.get(edit_key, {}).get('date', row['date'])
                                            if pd.isna(current_date):
                                                current_date = datetime.now().date()
                                            # Ensure it's a date object for date_input
                                            if isinstance(current_date, datetime):
                                                date_value = current_date.date()
                                            elif isinstance(current_date, pd.Timestamp):
                                                date_value = current_date.date()
                                            else:
                                                date_value = current_date
                                            date_input = st.date_input(
                                                "Date",
                                                value=date_value,
                                                key=f"date_{idx}"
                                            )
                                            
                                            # Amount input
                                            current_amount = st.session_state.transaction_edits.get(edit_key, {}).get('amount', row['amount'])
                                            amount_input = st.number_input(
                                                "Amount",
                                                value=current_amount or row['amount'] or 0.0,
                                                step=0.01,
                                                format="%.2f",
                                                key=f"amount_{idx}"
                                            )
                                            
                                            # Submit button for this transaction
                                            submitted = st.form_submit_button("💾 Save Changes", key=f"save_{idx}")
                                            
                                            if submitted:
                                                # Store the edit
                                                st.session_state.transaction_edits[edit_key] = {
                                                    'merchant': merchant_input,
                                                    'category': selected_category if selected_category != "➕ Create New Category" else "",
                                                    'date': date_input,
                                                    'amount': amount_input,
                                                    'is_new_category': selected_category == "➕ Create New Category"
                                                }
                                                st.rerun()
                                    
                                    with col3:
                                        # Action buttons
                                        if has_edits:
                                            if st.button("↩️ Reset", key=f"reset_{idx}"):
                                                if edit_key in st.session_state.transaction_edits:
                                                    del st.session_state.transaction_edits[edit_key]
                                                    st.rerun()
                                        else:
                                            st.write("")  # Empty space
                            
                            # Show edit summary
                            if edited_count > 0:
                                st.info(f"📝 **{edited_count} transactions have been edited**")
                            
                            # Handle new category creation
                            if st.session_state.transaction_edits:
                                for edit_key, edit_data in st.session_state.transaction_edits.items():
                                    if edit_data.get('is_new_category'):
                                        st.markdown("---")
                                        st.subheader("🆕 Create New Categories")
                                        
                                        # Extract unique new categories
                                        new_cats = set()
                                        for edit in st.session_state.transaction_edits.values():
                                            if edit.get('is_new_category') and edit.get('category'):
                                                new_cats.add(edit['category'])
                                        
                                        for new_cat in new_cats:
                                            with st.form(f"new_cat_form_{new_cat}"):
                                                st.markdown(f"**New Category: {new_cat}**")
                                                cat_desc = st.text_area(
                                                    "Description (optional)",
                                                    placeholder="Enter category description",
                                                    key=f"desc_{new_cat}"
                                                )
                                                
                                                if st.form_submit_button("✅ Create Category", key=f"create_{new_cat}"):
                                                    # Add to existing categories
                                                    existing_categories.append(new_cat)
                                                    # Add to new categories set
                                                    st.session_state.new_categories.add(new_cat)
                                                    st.success(f"✅ Created category: {new_cat}")
                                                    st.rerun()
                            
                            # Save all button
                            st.markdown("---")
                            st.subheader("💾 Save to Database")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("💾 Save All Transactions", type="primary", use_container_width=True):
                                    # Save to database with atomic transaction
                                    success_count, error_count, new_merchants, new_tags, new_categories = save_transactions_to_db_atomic(
                                        df_parsed, st.session_state.transaction_edits
                                    )
                                    
                                    if success_count > 0:
                                        # Clear edit state
                                        st.session_state.transaction_edits = {}
                                        st.session_state.new_categories = set()
                                        
                                        # Show success message with details
                                        st.success(f"✅ Successfully imported {success_count} transactions!")
                                        
                                        if new_merchants or new_tags or new_categories:
                                            st.info("🆕 **New items created:**")
                                            if new_merchants:
                                                st.write(f"- Merchants: {', '.join(new_merchants[:5])}{'...' if len(new_merchants) > 5 else ''}")
                                            if new_tags:
                                                st.write(f"- Tags: {', '.join(new_tags[:5])}{'...' if len(new_tags) > 5 else ''}")
                                            if new_categories:
                                                st.write(f"- Categories: {', '.join(new_categories[:5])}{'...' if len(new_categories) > 5 else ''}")
                                        
                                        if error_count > 0:
                                            st.warning(f"⚠️ {error_count} transactions had errors and were skipped.")
                                        
                                        # Show detailed import summary
                                        with st.expander("📋 Import Summary", expanded=True):
                                            st.markdown("**Import Statistics:**")
                                            summary_data = {
                                                "Total Processed": len(df_parsed),
                                                "Successfully Imported": success_count,
                                                "Errors/Skipped": error_count,
                                                "New Merchants": len(new_merchants),
                                                "New Tags": len(new_tags),
                                                "New Categories": len(new_categories)
                                            }
                                            st.json(summary_data)
                                            
                                            if new_merchants:
                                                st.markdown("**New Merchants Created:**")
                                                st.write(", ".join(new_merchants))
                                            
                                            if new_tags:
                                                st.markdown("**New Tags Created:**")
                                                st.write(", ".join(new_tags))
                                            
                                            if new_categories:
                                                st.markdown("**New Categories Created:**")
                                                st.write(", ".join(new_categories))
                                        
                                        # Navigate to Transactions page
                                        st.markdown("---")
                                        st.markdown("### 🎯 Next Steps")
                                        
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            if st.button("📋 View Transactions", type="secondary", use_container_width=True):
                                                st.session_state.page = 'transactions'
                                                st.success("✅ Redirecting to Transactions page...")
                                                st.rerun()
                                        
                                        with col2:
                                            if st.button("📤 Import Another File", use_container_width=True):
                                                # Clear the uploaded file state
                                                if 'uploaded_file' in st.session_state:
                                                    del st.session_state['uploaded_file']
                                                st.success("✅ Ready for another import!")
                                                st.rerun()
                                            
                                    else:
                                        st.error("❌ No transactions were imported. Please check for errors.")
                            
                            with col2:
                                if st.button("❌ Cancel & Reset", use_container_width=True):
                                    # Clear all edits
                                    st.session_state.transaction_edits = {}
                                    st.session_state.new_categories = set()
                                    st.success("✅ All edits cleared")
                                    st.rerun()
                            
                            # Show data types and summary
                            with st.expander("📊 Data Summary", expanded=False):
                                st.markdown("**Column Data Types:**")
                                st.json(df_parsed.dtypes.to_dict())
                                
                                st.markdown("**Sample Values:**")
                                for col in df_parsed.columns:
                                    unique_vals = df_parsed[col].dropna().unique()[:5]  # First 5 unique values
                                    st.write(f"**{col}**: {list(unique_vals)}")
                            
                            # Download section
                            st.markdown("---")
                            st.subheader("⬇️ Download Parsed Data")
                            
                            csv_data = utils.df_to_csv_bytes(df_parsed)
                            st.download_button(
                                label="📥 Download Parsed CSV",
                                data=csv_data,
                                file_name=f"parsed_{uploaded_file.name}",
                                mime="text/csv",
                                use_container_width=True
                            )
                    
                else:
                    # Show validation section (before mapping confirmation)
                    st.markdown("---")
                    
                    # -------------------------------------------------------
                    # Validation Section (before mapping)
                    # -------------------------------------------------------
                    st.subheader("✅ Column Validation")
                    
                    # Validate required columns
                    is_valid, missing_columns = utils.validate_transaction_columns(df)
                    
                    if is_valid:
                        st.success("✅ All required columns found!")
                        st.markdown("**Required columns detected:**")
                        st.markdown("- ✅ Date\n- ✅ Description\n- ✅ Amount")
                        
                        # Show available columns for mapping
                        st.markdown("**Available columns in your file:**")
                        for i, col in enumerate(df.columns, 1):
                            st.markdown(f"{i}. **{col}**")
                        
                        st.info("💡 **Auto-detection**: The form above will try to auto-select matching columns. Review and confirm the mapping.")
                        
                    else:
                        # Show missing columns error
                        st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                        st.warning(
                            "Please ensure your file contains the following columns:\n"
                            "- **Date** (or similar: transaction_date, date, txn_date)\n"
                            "- **Description** (or similar: merchant, narration, details)\n"
                            "- **Amount** (or similar: value, debit, credit, transaction_amount)"
                        )
                        
                        st.markdown("**Columns found in your file:**")
                        for col in df.columns:
                            st.markdown(f"- {col}")
    
    else:
        # -----------------------------------------------------------------------
        # No File Uploaded - Show Help
        # -----------------------------------------------------------------------
        st.info("👆 Upload a file to get started")
        
        # Show sample format
        with st.expander("📝 Sample CSV Format", expanded=False):
            st.markdown("### Example Bank Statement CSV")
            sample_data = {
                'Date': ['21/10/2025', '20/10/2025', '19/10/2025'],
                'Description': ['BigBasket - Groceries', 'HDFC Credit Card Bill', 'Salary Credit'],
                'Amount': [-2850.00, -12503.00, 75000.00],
                'Balance': [49557.50, 52407.50, 64910.50]
            }
            sample_df = pd.DataFrame(sample_data)
            st.dataframe(sample_df, use_container_width=True)
            
            # Download sample
            csv_sample = utils.df_to_csv_bytes(sample_df)
            st.download_button(
                label=" Download Sample CSV",
                data=csv_sample,
                file_name="sample_bank_statement.csv",
                mime="text/csv"
            )

def save_transactions_to_db_atomic(df_parsed: pd.DataFrame, edits: Dict[str, Dict]) -> Tuple[int, int, List[str], List[str], List[str]]:
    """
    Save parsed transactions to database with atomic transaction and auto-creation of entities.
    
    Args:
        df_parsed: Parsed DataFrame with transactions
        edits: Dictionary of transaction edits
        
    Returns:
        Tuple of (success_count, error_count, new_merchants, new_tags, new_categories)
    """
    from models import Transaction, Category, Tag
    from utils import check_duplicate_transaction, create_category_if_not_exists, create_tag_if_not_exists
    from db import DatabaseSession
    from datetime import datetime
    
    success_count = 0
    error_count = 0
    new_merchants = []
    new_tags = []
    new_categories = []
    
    try:
        with DatabaseSession() as db:
            # Collect all unique merchants, tags, and categories first
            unique_merchants = set()
            unique_tags = set()
            unique_categories = set()
            
            # Process each transaction to collect entities
            for idx, (_, row) in enumerate(df_parsed.iterrows()):
                edit_key = f"txn_{idx}"
                edit_data = edits.get(edit_key, {})
                
                # Extract data
                merchant = edit_data.get('merchant', row.get('merchant', row.get('description', '')))
                category_name = edit_data.get('category', row.get('category', ''))
                
                if merchant and merchant.strip():
                    unique_merchants.add(merchant.strip())
                
                if category_name and category_name.strip():
                    unique_categories.add(category_name.strip())
            
            # Pre-create/find all categories
            category_map = {}
            for cat_name in unique_categories:
                category_id = create_category_if_not_exists(cat_name)
                if category_id:
                    category_map[cat_name] = category_id
                    if cat_name not in [c[0] for c in db.query(Category.name).all()]:
                        new_categories.append(cat_name)
            
            # Pre-create/find all tags (if any tags are specified in edits)
            tag_map = {}
            for edit_data in edits.values():
                # Check if any tags are specified (for future tag support)
                # TODO: Add tag field to import form
                pass
            
            # Process each transaction for database insertion
            for idx, (_, row) in enumerate(df_parsed.iterrows()):
                try:
                    # Apply edits if they exist
                    edit_key = f"txn_{idx}"
                    edit_data = edits.get(edit_key, {})
                    
                    # Extract transaction data
                    date = edit_data.get('date', row['date'])
                    amount = edit_data.get('amount', row['amount'])
                    description = edit_data.get('merchant', row.get('merchant', row.get('description', '')))
                    category_name = edit_data.get('category', row.get('category', ''))
                    merchant = description  # Merchants are stored in the merchant field
                    
                    # Skip if no amount or amount is 0
                    if not amount or amount == 0:
                        continue
                    
                    # Check for duplicates
                    if check_duplicate_transaction(date, amount, description, category_name):
                        st.warning(f"⚠️ Potential duplicate detected for: {description} - ₹{amount:,.2f}")
                        continue
                    
                    # Get category ID
                    category_id = category_map.get(category_name)
                    
                    # Create transaction
                    transaction = Transaction(
                        user_id=1,  # TODO: Get actual user ID from session
                        account_id=1,  # TODO: Handle account selection
                        date=date,
                        merchant=merchant,
                        description=description,
                        amount=amount,
                        category_id=category_id,
                        is_manual=False,
                        is_investment=False
                    )
                    
                    db.add(transaction)
                    success_count += 1
                    
                    # Track new merchants (merchants are just strings, so we track unique ones)
                    # Note: Since merchants are stored as strings in transactions, we can't easily check for uniqueness
                    # across all existing transactions without a separate query. For now, we'll track them as "new"
                    # if they're not empty strings.
                    if merchant and merchant.strip() and merchant not in unique_merchants:
                        # This is a simplified check - in a real implementation, you'd want to check against existing merchants
                        new_merchants.append(merchant)
                    
                except Exception as e:
                    print(f"Error saving transaction {idx}: {e}")
                    error_count += 1
            
            # Commit all changes atomically
            db.commit()
            
    except Exception as e:
        print(f"Database error during atomic import: {e}")
        error_count = len(df_parsed)  # Mark all as errors
        success_count = 0
        
    return success_count, error_count, new_merchants, new_tags, new_categories

def show_settings():
    """
    Settings Page - Application configuration and preferences.
    
    TODO: Implement the following features:
    - User profile management
    - Password change
    - Currency and locale settings
    - Notification preferences
    - Data export/backup
    - Account deletion
    - Theme customization
    """
    
    st.title("⚙️ Settings")
    st.header("Settings – Coming Soon!")
    
    st.info(
        "This section will allow you to:\n\n"
        "✅ **Manage your profile** and account settings\n"
        "✅ **Change password** and security settings\n"
        "✅ **Configure preferences** (currency, timezone, etc.)\n"
        "✅ **Set notifications** and alerts\n"
        "✅ **Export/backup data** for safekeeping\n"
        "✅ **Customize theme** and appearance"
    )
    
    # Placeholder settings sections
    with st.expander("👤 Profile Settings", expanded=False):
        st.text_input("Username", value="demo_user", disabled=True)
        st.text_input("Email", value="demo@finco.app", disabled=True)
        st.caption("*Feature coming soon*")
    
    with st.expander("🌍 Preferences", expanded=False):
        st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"], disabled=True)
        st.selectbox("Date Format", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"], disabled=True)
        st.selectbox("Theme", ["Light", "Dark", "Auto"], disabled=True)
        st.caption("*Feature coming soon*")

def show_analytics_dashboard():
    """Display the analytics dashboard."""
    st.title("📊 Analytics Dashboard")
    
    # Get user ID from session
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("Please log in to view analytics.")
        return
    
    # Date range selection
    st.sidebar.header("Date Range")
    date_range = st.sidebar.selectbox(
        "Select Time Period",
        ["Last 30 Days", "Last 3 Months", "Last 6 Months", "Last Year", "Custom"],
        key="analytics_date_range"
    )
    
    # Set date range based on selection
    end_date = date.today()
    if date_range == "Last 30 Days":
        start_date = end_date - timedelta(days=30)
    elif date_range == "Last 3 Months":
        start_date = end_date - relativedelta(months=3)
    elif date_range == "Last 6 Months":
        start_date = end_date - relativedelta(months=6)
    elif date_range == "Last Year":
        start_date = end_date - relativedelta(years=1)
    else:  # Custom
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start Date", end_date - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", end_date)
    
    # Ensure start date is before end date
    if start_date > end_date:
        st.sidebar.error("Start date must be before end date")
        return
    
    # Get database session
    db = next(get_db())
    
    # Financial Health Score Card
    st.subheader("Financial Health Score")
    with st.spinner("Calculating financial health..."):
        health_data = get_financial_health_score(db, user_id)
    
    # Display score with color coding
    score = health_data['score']
    if score >= 80:
        score_color = "#2ecc71"  # Green
        score_emoji = "😊"
    elif score >= 50:
        score_color = "#f39c12"  # Orange
        score_emoji = "😐"
    else:
        score_color = "#e74c3c"  # Red
        score_emoji = "😟"
    
    # Score card
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Overall Score", 
            f"{score}/100 {score_emoji}",
            help="Based on savings rate, emergency fund, and debt-to-income ratio"
        )
    with col2:
        st.metric(
            "Savings Rate", 
            f"{health_data['savings_rate']:.1f}%",
            help="Percentage of income saved"
        )
    with col3:
        st.metric(
            "Emergency Fund", 
            f"{health_data['emergency_fund_months']:.1f} months",
            help="Months of expenses covered by savings"
        )
    with col4:
        st.metric(
            "Debt to Income", 
            f"{health_data['debt_to_income']*100:.1f}%",
            help="Lower is better"
        )
    
    # Income vs Expenses
    st.subheader("Income vs Expenses")
    with st.spinner("Loading income and expenses..."):
        income_expenses = get_income_vs_expenses(db, user_id, start_date, end_date)
        fig = create_income_vs_expenses_plot(income_expenses)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Spending Trends
    st.subheader("Spending Trends")
    with st.spinner("Analyzing spending trends..."):
        # Determine appropriate grouping based on date range
        days_diff = (end_date - start_date).days
        if days_diff <= 30:
            group_by = 'day'
        elif days_diff <= 180:
            group_by = 'week'
        else:
            group_by = 'month'
            
        trends_data = get_spending_trends(db, user_id, start_date, end_date, group_by)
        fig = create_spending_trends_plot(trends_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Spending by Category
    st.subheader("Spending by Category")
    with st.spinner("Categorizing expenses..."):
        spending_by_category = get_spending_by_category(db, user_id, start_date, end_date, CategoryType.EXPENSE)
        fig = create_spending_by_category_plot(spending_by_category)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Account Balances
    st.subheader("Account Balances")
    with st.spinner("Loading account information..."):
        accounts = get_account_balances(db, user_id)
        if accounts:
            # Create a donut chart for account balances
            df = pd.DataFrame(accounts)
            
            # Create the figure
            fig = px.pie(
                df,
                values='balance',
                names='name',
                title='Account Balances',
                hole=0.5,
                hover_data=['balance'],
                labels={'balance': 'Balance', 'name': 'Account'}
            )
            
            # Update layout
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='%{label}<br>%{value:$,.2f} (%{percent})<extra></extra>',
                textfont_size=12
            )
            
            fig.update_layout(
                margin=dict(t=40, b=10, l=10, r=10),
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show account balances in a table
            st.write("### Account Details")
            account_df = pd.DataFrame(accounts)[['name', 'balance', 'currency']]
            account_df['balance'] = account_df.apply(
                lambda x: f"{x['currency']} {x['balance']:,.2f}", 
                axis=1
            )
            account_df = account_df.rename(columns={
                'name': 'Account',
                'balance': 'Balance',
                'currency': 'Currency'
            })
            st.dataframe(
                account_df,
                column_config={
                    'Account': st.column_config.TextColumn("Account"),
                    'Balance': st.column_config.NumberColumn("Balance", format="$​%.2f"),
                    'Currency': st.column_config.TextColumn("Currency")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No account data available")
    
    # Add some space at the bottom
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """
    Main application entry point.
    
    This function:
    1. Initializes the database
    2. Renders the sidebar navigation
    3. Routes to the appropriate page based on user selection
    """
    # Set page config first
    st.set_page_config(
        page_title="FinCo - Personal Finance Tracker",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database first
    try:
        init_db()
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        st.stop()
    
    # Initialize session state for page routing
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'
    
    # Render sidebar
    try:
        render_sidebar()
    except Exception as e:
        st.sidebar.error("Error loading sidebar. Please refresh the page.")
        st.error(f"Application error: {str(e)}")
        return
    
    # -----------------------------------------------------------------------
    # Page Routing
    # -----------------------------------------------------------------------
    # Route to the appropriate page function based on session state
    page = st.session_state.page
    
    if page == 'dashboard':
        show_dashboard()
    elif page == 'transactions':
        show_transactions()
    elif page == 'budgets':
        show_budgets()
    elif page == 'goals':
        show_goals()
    elif page == 'investments':
        show_investments()
    elif page == 'reports':
        from reports import show_reports
        show_reports()
    elif page == 'import':
        show_import()
    elif page == 'settings':
        show_settings()
    else:
        # Default to dashboard for unknown pages
        show_dashboard()

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    # Set environment variable for SQLite to work in Streamlit Cloud
    import os
    os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"
    
    # Ensure the database directory exists
    os.makedirs("./data", exist_ok=True)
    
    # Set SQLite database path
    os.environ["DATABASE_URL"] = "sqlite:///./data/finance.db"
    
    # Run the app
    main()
