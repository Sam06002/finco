# Transaction Editing Guide - Import Statement Feature

## Overview

The Transaction Editing feature allows you to review and modify parsed transactions before importing them into your FinCo database. This ensures accuracy and helps you organize your financial data properly.

## Editing Workflow

### Step 1: Upload & Parse
1. Upload your bank statement (CSV, Excel, or PDF)
2. System processes and parses the data
3. Review the parsed transactions

### Step 2: Edit Transactions
For each transaction, you can edit:
- **Merchant Name** - Rename merchant/vendor name
- **Category** - Assign or create categories
- **Date** - Modify transaction date
- **Amount** - Adjust transaction amount

### Step 3: Review Changes
- Edited transactions are marked with 🔧 *Edited* badge
- View edit summary showing how many transactions modified
- Create new categories if needed

### Step 4: Save to Database
- Click "💾 Save All Transactions" to import
- System validates and saves to database
- Handles duplicates and creates new categories

## Editing Interface

### Transaction Card Layout

Each transaction is displayed in a card format:

```
┌─────────────────────────────────────────────────────────┐
│ Transaction 1    🔧 *Edited*                           │
│ Original: BigBasket - Groceries...                      │
│ ┌─────────────────┐ ┌──────────────┐ ┌─────────────┐ │
│ │ Merchant Name   │ │ Category     │ │ Date        │ │
│ │ [Text Input]    │ │ [Dropdown]   │ │ [Date Input]│ │
│ └─────────────────┘ └──────────────┘ └─────────────┘ │
│ ┌─────────────────┐ ┌──────────────┐ ┌─────────────┐ │
│ │ Amount          │ │ Save Changes │ │ Reset       │ │
│ │ [Number Input]  │ │ [Button]     │ │ [Button]    │ │
│ └─────────────────┘ └──────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Visual Indicators

#### Edited Transactions
- **🔧 *Edited*** badge appears next to transaction number
- Edit summary shows total edited count
- Individual edit forms are highlighted

#### Unedited Transactions
- Clean, minimal display
- Reset button only appears for edited transactions

## Field Editing Details

### 1. Merchant Name
**Purpose**: Rename merchants for better organization

**Default Value**: Parsed merchant name from file

**Examples**:
- `"BigBasket - Groceries"` → `"BigBasket"`
- `"SWIGGY FOOD DELIVERY"` → `"Swiggy"`
- `"HDFC Credit Card Bill"` → `"HDFC Credit Card"`

**Tips**:
- Use consistent naming (e.g., "Swiggy", not "SWIGGY")
- Keep names short but recognizable
- Use proper capitalization

### 2. Category
**Purpose**: Organize transactions into logical groups

**Options**:
- **Existing Categories**: Dropdown of all your categories
- **Create New**: "➕ Create New Category" option

**Default Value**: Parsed category from file (if available)

**Examples**:
- Food & Dining
- Transportation
- Utilities
- Entertainment
- Healthcare
- Shopping

**Creating New Categories**:
1. Select "➕ Create New Category"
2. Enter category name in the dropdown
3. Click "✅ Create Category" button
4. New category is saved for future use

### 3. Date
**Purpose**: Correct transaction dates if needed

**Default Value**: Parsed date from file

**Format**: DD/MM/YYYY (Indian format)

**Tips**:
- Use date picker for easy selection
- Correct any parsing errors
- Ensure dates are in correct order

### 4. Amount
**Purpose**: Fix amount parsing errors

**Default Value**: Parsed amount from file

**Format**: Decimal number (e.g., 2850.00)

**Tips**:
- Include decimal places for cents/paise
- Ensure correct sign (positive for income, negative for expenses)
- Fix currency symbol parsing errors

## Edit State Management

### Session State Variables

The system uses Streamlit session state to track edits:

```python
st.session_state.transaction_edits = {
    "txn_0": {
        "merchant": "BigBasket",
        "category": "Food & Dining",
        "date": datetime.date(2025, 10, 21),
        "amount": 2850.00
    },
    "txn_1": {
        "merchant": "HDFC Credit Card",
        "category": "Credit Card",
        "date": datetime.date(2025, 10, 20),
        "amount": -12503.00
    }
}

st.session_state.new_categories = {"New Category Name"}
```

### Edit Persistence

- Edits persist across page reruns
- Individual transaction saves update session state
- "Save All" clears edit state after successful import
- "Cancel & Reset" clears all edits

## Database Import Process

### Step 1: Validation
Before saving, the system validates:
- Required fields are present
- Amount is not zero
- Date is valid

### Step 2: Duplicate Detection
The system checks for potential duplicates:

#### Detection Criteria
- **Date Range**: ±1 day from transaction date
- **Amount Similarity**: ±1% of transaction amount
- **Description Match**: First 10 characters of description

#### Example Detection
```python
# If existing transaction:
# Date: 21/10/2025, Amount: ₹2,850.00, Description: "BigBasket"

# New transaction:
# Date: 21/10/2025, Amount: ₹2,850.00, Description: "BigBasket - Groceries"

# → DUPLICATE DETECTED
```

### Step 3: Category Handling
- **Existing Categories**: Links to existing category ID
- **New Categories**: Creates new category in database
- **No Category**: Saves transaction without category

### Step 4: Transaction Creation
Creates `Transaction` objects with:
- **user_id**: Current user ID (placeholder: 1)
- **account_id**: Default account (placeholder: 1)
- **date**: Transaction date
- **merchant**: Edited merchant name
- **description**: Original or edited description
- **amount**: Edited amount
- **category_id**: Category ID (if assigned)
- **is_manual**: False (imported from file)
- **is_investment**: False (regular transaction)

## Error Handling

### Common Import Errors

#### "Potential duplicate detected"
**Cause**: Similar transaction already exists
**Solution**: 
- Review the existing transaction
- Skip if it's indeed a duplicate
- Continue if it's a legitimate separate transaction

#### "No transactions were imported"
**Cause**: All transactions failed validation or were duplicates
**Solution**:
- Check transaction data for errors
- Ensure amounts are not zero
- Verify required fields are present

#### "Database error during import"
**Cause**: Database connection or constraint issues
**Solution**:
- Check database connection
- Ensure foreign key constraints are met
- Contact support for persistent issues

## Best Practices

### For Better Import Results

#### 1. Review Before Editing
- Check parsed data for accuracy
- Note any parsing errors
- Verify amounts and dates

#### 2. Consistent Naming
- Use consistent merchant names (e.g., "Swiggy", not "SWIGGY")
- Standardize category names
- Follow your existing naming conventions

#### 3. Category Strategy
- Create broad categories first (e.g., "Food", "Transport")
- Use sub-categories if needed (e.g., "Food - Dining Out")
- Don't create too many similar categories

#### 4. Amount Verification
- Double-check negative amounts for expenses
- Verify decimal places
- Ensure amounts match your records

#### 5. Date Accuracy
- Correct any date parsing errors
- Ensure dates are in logical order
- Check for weekend/weekday patterns

### Handling Special Cases

#### Credit Card Payments
- **Merchant**: "HDFC Credit Card" or "ICICI Credit Card"
- **Amount**: Negative (payment made)
- **Category**: "Credit Card" or "Debt Payment"

#### Salary Deposits
- **Merchant**: "Salary Credit" or company name
- **Amount**: Positive
- **Category**: "Income" or "Salary"

#### ATM Withdrawals
- **Merchant**: "ATM Withdrawal" or bank name
- **Amount**: Negative
- **Category**: "Cash Withdrawal"

#### EMI Payments
- **Merchant**: "Home Loan EMI" or "Car Loan EMI"
- **Amount**: Negative
- **Category**: "Loan Payment"

## Advanced Features

### Bulk Operations
Currently, each transaction must be edited individually. Future features may include:
- Select multiple transactions for bulk editing
- Apply category changes to multiple transactions
- Bulk date adjustments

### Edit History
Currently, edits are not tracked. Future features may include:
- Edit history for each transaction
- Rollback individual edits
- Audit trail for imported data

### Import Templates
Currently, no templates. Future features may include:
- Save column mapping for specific banks
- Template library for common statement formats
- Bank-specific parsing rules

## Troubleshooting

### Edit Not Saving
**Check**:
- Click "💾 Save Changes" button for each transaction
- Ensure form validation passes
- Check for JavaScript errors in browser console

### Category Not Creating
**Check**:
- Select "➕ Create New Category" from dropdown
- Enter category name in dropdown field
- Click "✅ Create Category" button

### Duplicate Detection Too Strict
**Issue**: Legitimate transactions being flagged as duplicates
**Solution**: 
- Review the existing transaction details
- Check if dates/amounts are very similar
- Continue with import if it's not actually a duplicate

### Amount Parsing Errors
**Check**:
- Ensure amount field is numeric in source file
- No currency symbols or text in amount column
- Decimal separator is correct (.)

## API Reference

### Database Functions

#### `save_transactions_to_db(df_parsed, edits)`
```python
"""Save parsed transactions to database with edit support."""
Args:
    df_parsed: pandas.DataFrame - Parsed transactions
    edits: Dict[str, Dict] - Transaction edits from session state
Returns:
    Tuple[int, int] - (success_count, error_count)
```

#### `check_duplicate_transaction(date, amount, description, category)`
```python
"""Check if suspiciously similar transaction exists."""
Args:
    date: datetime - Transaction date
    amount: float - Transaction amount
    description: str - Transaction description
    category: str - Transaction category
Returns:
    bool - True if potential duplicate found
```

#### `create_category_if_not_exists(name, description)`
```python
"""Create new category if it doesn't exist."""
Args:
    name: str - Category name
    description: str - Category description
Returns:
    int - Category ID
```

#### `get_existing_categories()`
```python
"""Get list of existing categories from database."""
Returns:
    List[str] - List of category names
```

## Performance Considerations

### Large Files
- Files with >1000 transactions may take time to process
- Edit interface shows only first few transactions initially
- Consider splitting large files for better performance

### Memory Usage
- All data kept in memory during editing session
- Edits stored in session state
- Memory cleared after successful import

### Database Performance
- Batch insert operations for efficiency
- Duplicate checking before each insert
- Transaction rollback on errors

## Future Enhancements

### Planned Features
1. **Bulk editing** - Edit multiple transactions at once
2. **Edit history** - Track all changes made during import
3. **Import templates** - Save mappings for common banks
4. **Smart suggestions** - Auto-suggest categories based on merchant
5. **Import scheduling** - Automated imports from bank APIs
6. **Advanced duplicate detection** - ML-based similarity matching
7. **Import reports** - Detailed success/failure reports

## Support

For questions or issues with transaction editing:
- Check this guide first
- Review IMPORT_GUIDE.md for general import help
- Check COLUMN_MAPPING_GUIDE.md for mapping issues
- Test with sample data first
- Contact: support@finco.app (future)

---

**Version**: 1.0.0
**Last Updated**: October 21, 2025
**Author**: FinCo Development Team
