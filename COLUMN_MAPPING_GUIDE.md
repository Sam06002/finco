# Column Mapping Guide - Import Statement Feature

## Overview

The Column Mapping feature allows you to map columns from your uploaded bank statement to standard FinCo transaction fields. This ensures your data is properly structured for import and analysis.

## Column Mapping Process

### Step 1: Upload File
1. Navigate to **Import Statement** page
2. Upload your bank statement (CSV, Excel, or PDF)
3. Review the data preview

### Step 2: Column Mapping Form
After uploading, you'll see a **Column Mapping** form with dropdowns for each field:

#### Required Fields
- **Date Column** - Transaction date (required)
- **Description Column** - Transaction details/merchant (required)
- **Amount Column** - Transaction amount (required)

#### Optional Fields
- **Merchant Column** - Merchant name (optional)
- **Account Column** - Account name/number (optional)
- **Category Column** - Transaction category (optional)

### Step 3: Auto-Detection
The system automatically detects column mappings based on common naming patterns. For example:
- Columns containing "date" → **Date**
- Columns containing "merchant" → **Merchant**
- Columns containing "amount" → **Amount**

### Step 4: Manual Mapping
If auto-detection doesn't work perfectly, you can manually select the correct column for each field using the dropdowns.

### Step 5: Confirm & Parse
1. Click **"✅ Confirm Mapping & Parse Data"**
2. System validates required fields are mapped
3. Data is parsed and standardized
4. Preview parsed transactions

## Supported Column Name Patterns

### Date Columns
The system recognizes these patterns:
- `date`, `transaction_date`, `txn_date`, `posting_date`, `value_date`
- `txn_date`, `trans_date`, `transaction_date`, `dt`, `datetime`
- `transaction_date`, `posting_date`

### Description Columns
The system recognizes these patterns:
- `description`, `merchant`, `narration`, `details`, `particulars`
- `party`, `payee`, `memo`, `reference`, `ref`, `remark`, `note`

### Amount Columns
The system recognizes these patterns:
- `amount`, `value`, `debit`, `credit`, `transaction_amount`
- `txn_amount`, `amt`, `sum`, `total`, `withdrawal`, `deposit`

### Merchant Columns
The system recognizes these patterns:
- `merchant`, `vendor`, `shop`, `store`, `supplier`, `party_name`
- `merchant_name`, `brand`, `company`, `business`

### Account Columns
The system recognizes these patterns:
- `account`, `account_no`, `account_number`, `acc_no`, `acc_number`
- `bank_account`, `account_name`, `acct`

### Category Columns
The system recognizes these patterns:
- `category`, `type`, `class`, `group`, `tag`, `classification`
- `expense_type`, `income_type`, `cat`

## Data Parsing & Standardization

### Date Parsing
The system handles multiple date formats:

#### Supported Formats
- **DD/MM/YYYY** - `21/10/2025`
- **MM/DD/YYYY** - `10/21/2025`
- **YYYY-MM-DD** - `2025-10-21`
- **DD-MM-YYYY** - `21-10-2025`
- **YYYY/MM/DD** - `2025/10/21`
- **DD.MM.YYYY** - `21.10.2025`
- **MM-DD-YYYY** - `10-21-2025`
- **DD Mon YYYY** - `21 Oct 2025`
- **DD Month YYYY** - `21 October 2025`

#### Automatic Detection
The system tries each format in order until one works. If none work, it falls back to pandas `to_datetime()` with error handling.

### Amount Parsing
The system handles various amount formats:

#### Supported Formats
- **Standard**: `1234.56`, `-1234.56`
- **With commas**: `1,234.56`, `-1,234.56`
- **With currency**: `₹1,234.56`, `$1,234.56`
- **Parentheses**: `(1,234.56)` for negative amounts
- **Debit/Credit**: `1,234.56 CR`, `1,234.56 DR`

#### Processing Steps
1. Remove currency symbols (₹, $, €, £, ¥)
2. Remove commas and spaces
3. Handle parentheses for negative amounts
4. Process DR/CR indicators
5. Convert to float

### Text Field Cleaning
Text fields are cleaned and standardized:

#### Processing Steps
1. Strip leading/trailing whitespace
2. Remove extra internal spaces
3. Convert to title case (capitalize first letter of each word)
4. Handle null values

#### Examples
- `"  bigbasket   groceries  "` → `"Bigbasket Groceries"`
- `"swiggy"` → `"Swiggy"`
- `None` → `""`

## Preview & Validation

### Before Mapping
- ✅ **Column validation** - Check required columns exist
- 📊 **Data preview** - Show first 10 rows
- 📋 **Column information** - Data types, null counts

### After Mapping
- ✅ **Required field validation** - Ensure Date, Description, Amount are mapped
- 🔄 **Data parsing** - Convert to proper Python types
- 📋 **Parsed preview** - Show standardized transactions
- 📊 **Summary statistics** - Income/expense counts, totals
- 📋 **Data summary** - Column types, sample values

## Error Handling

### Common Issues

#### "Missing required columns"
**Solution**: Ensure your file has Date, Description, and Amount columns. Check column names and try alternative spellings.

#### "Date parsing failed"
**Solution**:
- Check date format in your file
- Ensure dates are in a standard format
- Try different date formats

#### "Amount parsing failed"
**Solution**:
- Check for currency symbols that need removal
- Ensure amounts are numeric (no text)
- Look for parentheses or DR/CR indicators

#### "Auto-detection didn't work"
**Solution**: Manually select the correct columns using the dropdowns. The system will remember your preferences for future imports.

## Indian Bank Statement Formats

### HDFC Bank
```csv
Date,Narration,Chq./Ref.No.,Value Date,Withdrawal Amt.,Deposit Amt.,Closing Balance
21/10/2025,UPI/BigBasket,UPI123456,21/10/2025,2850.00,,49557.50
```

**Mapping:**
- Date: `Date`
- Description: `Narration`
- Amount: `Withdrawal Amt.` (debit) or `Deposit Amt.` (credit)

### ICICI Bank
```csv
Transaction Date,Value Date,Description,Debit,Credit,Balance
21/10/2025,21/10/2025,UPI-BigBasket,2850.00,,49557.50
```

**Mapping:**
- Date: `Transaction Date`
- Description: `Description`
- Amount: `Debit` (negative) or `Credit` (positive)

### SBI (State Bank of India)
```csv
Txn Date,Value Date,Description,Ref No./Cheque No.,Debit,Credit,Balance
21-Oct-2025,21-Oct-2025,UPI/BigBasket,202510210001,2850.00,,49557.50
```

**Mapping:**
- Date: `Txn Date`
- Description: `Description`
- Amount: `Debit` (negative) or `Credit` (positive)

### Axis Bank
```csv
Date,Particulars,Withdrawals,Deposits,Balance
21/10/2025,UPI-BigBasket Groceries,2850.00,,49557.50
```

**Mapping:**
- Date: `Date`
- Description: `Particulars`
- Amount: `Withdrawals` (negative) or `Deposits` (positive)

## Advanced Features

### Multi-Column Amount Mapping
Some banks split amounts into separate debit/credit columns. The system handles this by:
1. Auto-detecting debit/credit columns
2. Converting to single amount column
3. Negative for debits, positive for credits

### Date Format Detection
The system tries multiple date formats and selects the best match based on successful parsing.

### Fuzzy Column Matching
If exact matches aren't found, the system looks for columns containing keywords:
- Date: columns with "date", "txn", "value", "posting"
- Description: columns with "desc", "merchant", "narration", "details"
- Amount: columns with "amount", "debit", "credit", "value"

## API Reference

### `auto_detect_column_mapping(columns)`
```python
"""Auto-detect column mappings from DataFrame columns."""
Args:
    columns: pandas.Index of column names
Returns:
    Dict[str, int] - field -> column_index (1-based for selectbox)
```

### `parse_and_standardize_dataframe(df, date_col, desc_col, amount_col, ...)`
```python
"""Parse and standardize DataFrame based on column mapping."""
Args:
    df: pandas.DataFrame - Original data
    date_col: str - Date column name
    desc_col: str - Description column name
    amount_col: str - Amount column name
    merchant_col: str - Merchant column (optional)
    account_col: str - Account column (optional)
    category_col: str - Category column (optional)
Returns:
    pandas.DataFrame - Standardized data with parsed types
```

### `parse_dates(date_series)`
```python
"""Parse various date formats into datetime objects."""
Args:
    date_series: pandas.Series of date strings
Returns:
    pandas.Series of parsed datetime objects
```

### `parse_amounts(amount_series)`
```python
"""Parse various amount formats into float values."""
Args:
    amount_series: pandas.Series of amount strings
Returns:
    pandas.Series of parsed float amounts
```

## Troubleshooting

### Column Mapping Issues

#### Auto-detection failed
**Manual Solution**: Use dropdowns to manually select correct columns

#### Required field not found
**Check**:
- Column exists in your file
- Spelling matches (case-insensitive)
- Column isn't empty

#### Date parsing errors
**Check**:
- Date format in your file
- Try different date format patterns
- Ensure dates are consistent

#### Amount parsing errors
**Check**:
- No currency symbols in amount column
- No text in amount column
- Proper negative/positive indicators

### Performance Issues

#### Large files slow to process
**Solution**:
- Files > 1000 rows may take time
- Consider splitting large files
- Future: Implement batch processing

#### Memory issues
**Solution**:
- Large files processed in chunks
- Memory cleared after processing
- Contact support for very large files

## Future Enhancements

### Planned Features
1. **Column mapping templates** - Save mappings for common banks
2. **Smart suggestions** - Learn from user corrections
3. **Batch processing** - Handle multiple files
4. **Advanced parsing** - Handle complex bank formats
5. **Preview before parsing** - Show what data will look like
6. **Export mapping** - Save column mapping for reuse

## Support

For questions or issues with column mapping:
- Check this guide first
- Review the IMPORT_GUIDE.md for general import help
- Test with the sample CSV file
- Contact: support@finco.app (future)

---

**Version**: 1.0.0
**Last Updated**: October 21, 2025
**Author**: FinCo Development Team
