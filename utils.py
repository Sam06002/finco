import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
import pdfplumber
import io
import tempfile
from dateutil.relativedelta import relativedelta
from calendar import month_name
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from models import Transaction, Category, Account
from db import get_db_session

def parse_date(date_str: str, format: str = "%Y-%m-%d") -> datetime:
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str, format)
    except (ValueError, TypeError):
        return None

def format_currency(amount: float) -> str:
    """Format number as currency in Indian Rupees"""
    return f"₹{amount:,.2f}"

def format_indian_currency(amount: float) -> str:
    """
    Format number as currency in Indian Rupees with Indian numbering system.
    Uses lakhs and crores notation (e.g., ₹1,23,45,678.90)
    """
    if amount < 0:
        return f"-₹{format_indian_number(abs(amount))}"
    return f"₹{format_indian_number(amount)}"

def format_indian_number(num: float) -> str:
    """
    Format number in Indian numbering system.
    Example: 12345678.90 -> 1,23,45,678.90
    """
    s = f"{num:.2f}"
    if '.' in s:
        integer_part, decimal_part = s.split('.')
    else:
        integer_part = s
        decimal_part = "00"
    
    # Reverse the integer part
    integer_part = integer_part[::-1]
    
    # Add commas in Indian style (first 3 digits, then every 2)
    formatted = ""
    for i, digit in enumerate(integer_part):
        if i == 3:
            formatted += ","
        elif i > 3 and (i - 3) % 2 == 0:
            formatted += ","
        formatted += digit
    
    # Reverse back and add decimal part
    return formatted[::-1] + "." + decimal_part

def read_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to CSV bytes"""
    return df.to_csv(index=False).encode('utf-8')

def calculate_summary(transactions: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate summary statistics for transactions"""
    if not transactions:
        return {"total_income": 0, "total_expenses": 0, "net_balance": 0}
    
    df = pd.DataFrame(transactions)
    total_income = df[df['type'] == 'income']['amount'].sum()
    total_expenses = df[df['type'] == 'expense']['amount'].sum()
    
    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_balance": round(total_income - total_expenses, 2)
    }

# ============================================================================
# FILE UPLOAD & STATEMENT IMPORT FUNCTIONS
# ============================================================================

def read_csv_file(file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Read CSV file and return DataFrame.
    
    Args:
        file: File object from Streamlit file_uploader
        
    Returns:
        tuple: (DataFrame, error_message)
        If successful, error_message is None
        If failed, DataFrame is None
    """
    try:
        # Try different encodings
        try:
            df = pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            file.seek(0)  # Reset file pointer
            df = pd.read_csv(file, encoding='latin-1')
        
        if df.empty:
            return None, "CSV file is empty"
        
        return df, None
    except Exception as e:
        return None, f"Error reading CSV: {str(e)}"

def read_excel_file(file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Read Excel file and return DataFrame.
    
    Args:
        file: File object from Streamlit file_uploader
        
    Returns:
        tuple: (DataFrame, error_message)
        If successful, error_message is None
        If failed, DataFrame is None
    """
    try:
        # Read Excel file (first sheet by default)
        df = pd.read_excel(file, engine='openpyxl')
        
        if df.empty:
            return None, "Excel file is empty"
        
        return df, None
    except Exception as e:
        return None, f"Error reading Excel: {str(e)}"

def read_pdf_file(file) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[str]]:
    """
    Read PDF file and attempt to extract tables or text.
    
    Args:
        file: File object from Streamlit file_uploader
        
    Returns:
        tuple: (DataFrame, text_content, error_message)
        - If tables found, DataFrame contains first table
        - text_content contains first page text
        - If failed, both DataFrame and text are None
    """
    try:
        # Read PDF with pdfplumber
        pdf = pdfplumber.open(file)
        
        if len(pdf.pages) == 0:
            return None, None, "PDF file has no pages"
        
        # Get first page
        first_page = pdf.pages[0]
        
        # Try to extract tables
        tables = first_page.extract_tables()
        df = None
        
        if tables:
            # Convert first table to DataFrame
            table_data = tables[0]
            if len(table_data) > 1:
                # First row as headers
                df = pd.DataFrame(table_data[1:], columns=table_data[0])
        
        # Extract text from first page
        text_content = first_page.extract_text()
        
        pdf.close()
        
        if df is None and not text_content:
            return None, None, "Could not extract tables or text from PDF"
        
        return df, text_content, None
        
    except Exception as e:
        return None, None, f"Error reading PDF: {str(e)}"

def validate_transaction_columns(df: pd.DataFrame, required_columns: List[str] = None) -> Tuple[bool, List[str]]:
    """
    Validate that DataFrame has required columns for transactions.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names (case-insensitive)
                         Default: ['date', 'description', 'amount']
    
    Returns:
        tuple: (is_valid, missing_columns)
        - is_valid: True if all required columns found
        - missing_columns: List of missing column names
    """
    if required_columns is None:
        required_columns = ['date', 'description', 'amount']
    
    # Convert all column names to lowercase for comparison
    df_columns_lower = [col.lower().strip() for col in df.columns]
    
    missing = []
    for req_col in required_columns:
        req_col_lower = req_col.lower()
        if req_col_lower not in df_columns_lower:
            missing.append(req_col)
    
    return len(missing) == 0, missing

def clean_and_process_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and process imported transaction data.
    
    TODO: Implement the following:
    - Standardize column names
    - Parse and validate dates
    - Clean amount values (remove currency symbols, convert to float)
    - Remove duplicates
    - Handle missing values
    - Categorize transactions (auto-categorization)
    - Detect transaction type (income/expense)
    - Add metadata (import date, source file)
    
    Args:
        df: Raw DataFrame from imported file
        
    Returns:
        Cleaned DataFrame ready for database import
    """
    # STUB: This function will be implemented later
    # For now, just return the original DataFrame
    
    # Basic cleaning (placeholder)
    df_clean = df.copy()
    
    # Strip whitespace from column names
    df_clean.columns = [col.strip() for col in df_clean.columns]
    
    # Remove completely empty rows
    df_clean = df_clean.dropna(how='all')
    
    return df_clean

def save_uploaded_file_temp(uploaded_file) -> str:
    """
    Save uploaded file to temporary directory.
    
    Args:
        uploaded_file: File object from Streamlit file_uploader
        
    Returns:
        Path to saved temporary file
    """
    try:
        # Create temp directory if it doesn't exist
        temp_dir = tempfile.gettempdir()
        
        # Generate unique filename
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Write file
        with open(temp_file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return temp_file_path
    except Exception as e:
        raise Exception(f"Error saving file: {str(e)}")

# ============================================================================
# DATABASE & IMPORT UTILITIES
# ============================================================================

def get_existing_categories() -> List[str]:
    """
    Get list of existing categories from database.
    
    Returns:
        List of category names
    """
    from db import DatabaseSession
    from models import Category
    
    try:
        with DatabaseSession() as db:
            categories = db.query(Category.name).distinct().all()
            return [cat[0] for cat in categories if cat[0]]
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []

def check_duplicate_transaction(date: datetime, amount: float, description: str, category: str = None) -> bool:
    """
    Check if a suspiciously similar transaction already exists.
    
    Args:
        date: Transaction date
        amount: Transaction amount
        description: Transaction description
        category: Transaction category
        
    Returns:
        True if potential duplicate found
    """
    from db import DatabaseSession
    from models import Transaction
    
    try:
        with DatabaseSession() as db:
            # Check for transactions within 1 day of the same date
            # with similar amount (±1%) and description
            date_range = [date - timedelta(days=1), date + timedelta(days=1)]
            
            # Similar amount check (±1%)
            amount_tolerance = abs(amount) * 0.01
            
            query = db.query(Transaction).filter(
                Transaction.date.between(date_range[0], date_range[1]),
                Transaction.amount.between(amount - amount_tolerance, amount + amount_tolerance)
            )
            
            # If category is provided, also check category match
            if category:
                query = query.filter(Transaction.category_id.isnot(None))
            
            existing_transactions = query.all()
            
            # Check for description similarity (basic check)
            for txn in existing_transactions:
                if txn.description and description:
                    # Simple similarity check (can be improved)
                    if len(txn.description) > 10 and len(description) > 10:
                        if txn.description.lower()[:10] == description.lower()[:10]:
                            return True
            
            return False
            
    except Exception as e:
        print(f"Error checking duplicates: {e}")
        return False

def create_category_if_not_exists(name: str, description: str = None) -> int:
    """
    Create a new category if it doesn't exist.
    
    Args:
        name: Category name
        description: Category description
        
    Returns:
        Category ID
    """
    from db import DatabaseSession
    from models import Category
    
    try:
        with DatabaseSession() as db:
            # Check if category already exists
            existing = db.query(Category).filter(Category.name == name).first()
            if existing:
                return existing.category_id
            
            # Create new category
            new_category = Category(
                name=name,
                type="expense",  # Default to expense, can be changed later
                description=description
            )
            db.add(new_category)
            db.flush()  # Get the ID
            
            return new_category.category_id
            
    except Exception as e:
        print(f"Error creating category: {e}")
        return None

def create_tag_if_not_exists(label: str) -> int:
    """
    Create a new tag if it doesn't exist.
    
    Args:
        label: Tag label
        
    Returns:
        Tag ID
    """
    from db import DatabaseSession
    from models import Tag
    
    try:
        with DatabaseSession() as db:
            # Check if tag already exists
            existing = db.query(Tag).filter(Tag.label == label).first()
            if existing:
                return existing.tag_id
            
            # Create new tag
            new_tag = Tag(
                label=label
            )
            db.add(new_tag)
            db.flush()  # Get the ID
            
            return new_tag.tag_id
            
    except Exception as e:
        print(f"Error creating tag: {e}")
        return None

def auto_detect_column_mapping(columns: pd.Index) -> Dict[str, int]:
    """
    Auto-detect column mappings based on column names.
    
    Args:
        columns: DataFrame column names
        
    Returns:
        Dict mapping field names to column indices (0-based)
        Empty dict if no matches found
    """
    # Convert columns to lowercase for matching
    columns_lower = [col.lower().strip() for col in columns]
    
    # Define mapping patterns for each field
    field_patterns = {
        'date': [
            'date', 'transaction_date', 'txn_date', 'posting_date', 'value_date',
            'txn_date', 'trans_date', 'transaction_date', 'dt', 'datetime'
        ],
        'description': [
            'description', 'merchant', 'narration', 'details', 'particulars',
            'party', 'payee', 'memo', 'reference', 'ref', 'remark', 'note'
        ],
        'amount': [
            'amount', 'value', 'debit', 'credit', 'transaction_amount',
            'txn_amount', 'amt', 'sum', 'total', 'withdrawal', 'deposit'
        ],
        'merchant': [
            'merchant', 'vendor', 'shop', 'store', 'supplier', 'party_name',
            'merchant_name', 'brand', 'company', 'business'
        ],
        'account': [
            'account', 'account_no', 'account_number', 'acc_no', 'acc_number',
            'bank_account', 'account_name', 'acct'
        ],
        'category': [
            'category', 'type', 'class', 'group', 'tag', 'classification',
            'expense_type', 'income_type', 'cat'
        ]
    }
    
    mappings = {}
    
    # Find matches for each field
    for field, patterns in field_patterns.items():
        for i, col in enumerate(columns_lower):
            if any(pattern in col for pattern in patterns):
                mappings[field] = i + 1  # 1-based index for selectbox
                break
    
    return mappings

def parse_and_standardize_dataframe(
    df: pd.DataFrame,
    date_col: str,
    desc_col: str,
    amount_col: str,
    merchant_col: str = "",
    account_col: str = "",
    category_col: str = ""
) -> pd.DataFrame:
    """
    Parse and standardize DataFrame based on column mapping.
    
    Args:
        df: Original DataFrame
        date_col: Name of date column
        desc_col: Name of description column
        amount_col: Name of amount column
        merchant_col: Name of merchant column (optional)
        account_col: Name of account column (optional)
        category_col: Name of category column (optional)
        
    Returns:
        Standardized DataFrame with parsed data types
    """
    # Create a copy to avoid modifying original
    df_parsed = df.copy()
    
    # -----------------------------------------------------------------------
    # Rename columns to standard names
    # -----------------------------------------------------------------------
    column_mapping = {}
    
    if date_col and date_col in df.columns:
        column_mapping[date_col] = 'date'
    if desc_col and desc_col in df.columns:
        column_mapping[desc_col] = 'description'
    if amount_col and amount_col in df.columns:
        column_mapping[amount_col] = 'amount'
    if merchant_col and merchant_col in df.columns:
        column_mapping[merchant_col] = 'merchant'
    if account_col and account_col in df.columns:
        column_mapping[account_col] = 'account'
    if category_col and category_col in df.columns:
        column_mapping[category_col] = 'category'
    
    # Rename columns
    df_parsed = df_parsed.rename(columns=column_mapping)
    
    # Keep only mapped columns
    mapped_cols = [col for col in ['date', 'description', 'amount', 'merchant', 'account', 'category'] if col in df_parsed.columns]
    df_parsed = df_parsed[mapped_cols]
    
    # -----------------------------------------------------------------------
    # Parse and standardize data types
    # -----------------------------------------------------------------------
    
    # Parse dates
    if 'date' in df_parsed.columns:
        df_parsed['date'] = parse_dates(df_parsed['date'])
    
    # Parse amounts
    if 'amount' in df_parsed.columns:
        df_parsed['amount'] = parse_amounts(df_parsed['amount'])
    
    # Clean text fields
    for col in ['description', 'merchant', 'account', 'category']:
        if col in df_parsed.columns:
            df_parsed[col] = clean_text_field(df_parsed[col])
    
    # -----------------------------------------------------------------------
    # Add metadata columns
    # -----------------------------------------------------------------------
    df_parsed['import_timestamp'] = datetime.now()
    df_parsed['source_file'] = 'uploaded_statement'
    df_parsed['is_imported'] = True
    
    return df_parsed

def parse_dates(date_series: pd.Series) -> pd.Series:
    """
    Parse various date formats into datetime objects.
    
    Args:
        date_series: Series of date strings
        
    Returns:
        Series of parsed datetime objects
    """
    def parse_single_date(date_str):
        if pd.isna(date_str):
            return pd.NaT
        
        # Convert to string if not already
        date_str = str(date_str).strip()
        
        # Try various date formats
        formats = [
            '%d/%m/%Y',        # 21/10/2025
            '%m/%d/%Y',        # 10/21/2025
            '%Y-%m-%d',        # 2025-10-21
            '%d-%m-%Y',        # 21-10-2025
            '%Y/%m/%d',        # 2025/10/21
            '%d.%m.%Y',        # 21.10.2025
            '%m-%d-%Y',        # 10-21-2025
            '%d %b %Y',        # 21 Oct 2025
            '%d %B %Y',        # 21 October 2025
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try pandas to_datetime as last resort
        try:
            return pd.to_datetime(date_str, errors='coerce')
        except:
            return pd.NaT
    
    return date_series.apply(parse_single_date)

def parse_amounts(amount_series: pd.Series) -> pd.Series:
    """
    Parse various amount formats into float values.
    
    Args:
        amount_series: Series of amount strings
        
    Returns:
        Series of parsed float amounts
    """
    def parse_single_amount(amount_str):
        if pd.isna(amount_str):
            return 0.0
        
        # Convert to string
        amount_str = str(amount_str).strip()
        
        # Handle negative amounts in parentheses
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        # Remove currency symbols and commas
        import re
        amount_str = re.sub(r'[₹$€£¥,\s]', '', amount_str)
        
        # Handle debit/credit indicators
        if 'CR' in amount_str.upper() or 'CREDIT' in amount_str.upper():
            amount_str = amount_str.replace('CR', '').replace('CREDIT', '')
        elif 'DR' in amount_str.upper() or 'DEBIT' in amount_str.upper():
            amount_str = '-' + amount_str.replace('DR', '').replace('DEBIT', '')
        
        try:
            return float(amount_str)
        except ValueError:
            return 0.0
    
    return amount_series.apply(parse_single_amount)

def clean_text_field(text_series: pd.Series):
    """
    Clean text fields by removing extra whitespace and converting to title case.
    
    Args:
        text_series: Series of text values
        
    Returns:
        Series of cleaned text values
    """
    if text_series is None or text_series.empty:
        return text_series
        
    return text_series.str.strip().str.title().replace(r'\s+', ' ', regex=True)

# ============================================================================
# DASHBOARD & REPORTS UTILITIES
# ============================================================================

def get_month_name(month_num: int) -> str:
    """Convert month number to full month name"""
    return month_name[int(month_num)]

def get_current_month_range() -> tuple[datetime, datetime]:
    """Get start and end dates of current month"""
    today = datetime.now()
    start = today.replace(day=1)
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    end = next_month - timedelta(days=1)
    return start, end

def get_monthly_summary(user_id: int, year: int = None, month: int = None) -> dict:
    """
    Get monthly summary (income, expenses, savings) for a user
    
    Args:
        user_id: ID of the user
        year: Year to filter (default: current year)
        month: Month to filter (1-12, default: current month)
        
    Returns:
        Dictionary with income, expenses, and savings
    """
    from models import CategoryType
    
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    
    with get_db_session() as db:
        # Get income (positive amounts from income categories)
        income = db.query(func.sum(Transaction.amount)).join(
            Category, Transaction.category_id == Category.category_id
        ).filter(
            Transaction.user_id == user_id,
            Category.type == CategoryType.INCOME,
            extract('year', Transaction.date) == year,
            extract('month', Transaction.date) == month
        ).scalar() or 0.0
        
        # Get expenses (amounts from expense categories)
        expenses = db.query(func.sum(Transaction.amount)).join(
            Category, Transaction.category_id == Category.category_id
        ).filter(
            Transaction.user_id == user_id,
            Category.type == CategoryType.EXPENSE,
            extract('year', Transaction.date) == year,
            extract('month', Transaction.date) == month
        ).scalar() or 0.0
        
        return {
            'income': float(abs(income)),
            'expenses': float(abs(expenses)),
            'savings': float(abs(income) - abs(expenses)),
            'savings_rate': (abs(income) - abs(expenses)) / abs(income) * 100 if income > 0 else 0
        }

def get_transactions_by_month(user_id: int, year: int = None, month: int = None, 
                           transaction_type: str = None) -> List[Dict]:
    """
    Get transactions for a specific month
    
    Args:
        user_id: ID of the user
        year: Year to filter (default: current year)
        month: Month to filter (1-12, default: current month)
        transaction_type: Type of transactions to include ('income' or 'expense', None for all)
        
    Returns:
        List of transaction dictionaries
    """
    from models import CategoryType
    
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    
    with get_db_session() as db:
        query = db.query(
            Transaction,
            Category.name.label('category_name'),
            Category.type.label('category_type'),
            Account.account_name
        ).join(
            Category, Transaction.category_id == Category.category_id, isouter=True
        ).join(
            Account, Transaction.account_id == Account.account_id
        ).filter(
            Transaction.user_id == user_id,
            extract('year', Transaction.date) == year,
            extract('month', Transaction.date) == month
        ).order_by(
            Transaction.date.desc()
        )
        
        if transaction_type:
            if transaction_type == 'income':
                query = query.filter(Category.type == CategoryType.INCOME)
            elif transaction_type == 'expense':
                query = query.filter(Category.type == CategoryType.EXPENSE)
            
        results = query.all()
        
        return [{
            'id': t.Transaction.transaction_id,
            'date': t.Transaction.date,
            'amount': float(abs(t.Transaction.amount)),
            'description': t.Transaction.description or '',
            'category': t.category_name or 'Uncategorized',
            'account': t.account_name,
            'type': t.category_type.value if t.category_type else 'unknown'
        } for t in results]

def get_category_totals(user_id: int, start_date: datetime = None, end_date: datetime = None, 
                       transaction_type: str = 'expense') -> List[Tuple[str, float]]:
    """
    Get category-wise totals for a user within a date range
    
    Args:
        user_id: ID of the user
        start_date: Start date for filtering
        end_date: End date for filtering
        transaction_type: Type of transactions to include ('income' or 'expense')
        
    Returns:
        List of tuples (category_name, total_amount)
    """
    from models import CategoryType
    
    with get_db_session() as db:
        query = db.query(
            Category.name,
            func.sum(func.abs(Transaction.amount)).label('total')
        ).join(
            Transaction, Category.category_id == Transaction.category_id
        ).filter(
            Transaction.user_id == user_id
        )
        
        # Filter by category type
        if transaction_type == 'income':
            query = query.filter(Category.type == CategoryType.INCOME)
        elif transaction_type == 'expense':
            query = query.filter(Category.type == CategoryType.EXPENSE)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
            
        return query.group_by(Category.name).order_by(func.sum(func.abs(Transaction.amount)).desc()).all()
