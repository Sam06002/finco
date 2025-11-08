# Import Statement Guide

## Overview

The Import Statement feature allows you to import transactions from bank statements in various formats (CSV, Excel, PDF) into your FinCo application.

## Supported File Formats

### 1. CSV Files (.csv)
- Most common format exported by banks
- Easiest to work with
- Supports UTF-8 and Latin-1 encoding

### 2. Excel Files (.xlsx, .xls)
- Spreadsheet format
- First sheet is automatically imported
- Supports both old (.xls) and new (.xlsx) formats

### 3. PDF Files (.pdf)
- Bank statement PDFs with table formatting
- Extracts tables automatically using pdfplumber
- If no tables found, shows text content
- Works best with well-formatted PDFs

## Required Columns

Your file **must** contain at least these columns (case-insensitive):

| Column | Description | Example Values |
|--------|-------------|----------------|
| **Date** | Transaction date | 21/10/2025, 2025-10-21 |
| **Description** | Transaction description/merchant | "BigBasket - Groceries", "Salary Credit" |
| **Amount** | Transaction amount | -2850.00, 75000.00 |

**Note**: Column names are case-insensitive and whitespace is trimmed.

### Alternative Column Names

The system recognizes these alternative names:

- **Date**: `date`, `transaction_date`, `txn_date`, `posting_date`
- **Description**: `description`, `merchant`, `narration`, `details`, `particulars`
- **Amount**: `amount`, `value`, `debit`, `credit`, `transaction_amount`

## Optional Columns

These columns will be used if present:

- **Balance** - Account balance after transaction
- **Category** - Transaction category
- **Type** - Transaction type (debit/credit, income/expense)
- **Reference** - Reference number
- **Account** - Account name/number
- **Notes** - Additional notes

## File Format Examples

### CSV Format

```csv
Date,Description,Amount,Balance
21/10/2025,BigBasket - Groceries,-2850.00,49557.50
20/10/2025,HDFC Credit Card Bill,-12503.00,52407.50
19/10/2025,Salary Credit,75000.00,64910.50
18/10/2025,Swiggy Food Delivery,-850.00,-10089.50
17/10/2025,Metro Card Recharge,-500.00,-9239.50
```

### Excel Format

Same as CSV but in Excel spreadsheet format (.xlsx or .xls)

| Date | Description | Amount | Balance |
|------|-------------|--------|---------|
| 21/10/2025 | BigBasket - Groceries | -2850.00 | 49557.50 |
| 20/10/2025 | HDFC Credit Card Bill | -12503.00 | 52407.50 |
| 19/10/2025 | Salary Credit | 75000.00 | 64910.50 |

### PDF Format

Bank statements with clear table formatting work best:

```
Transaction Statement
Account: 1234567890
Period: October 2025

Date        Description              Debit      Credit     Balance
21/10/2025  BigBasket - Groceries    2,850.00              49,557.50
20/10/2025  Credit Card Bill        12,503.00              52,407.50
19/10/2025  Salary Credit                      75,000.00   64,910.50
```

## Usage Instructions

### Step 1: Navigate to Import Page
1. Open FinCo application
2. Click on "📄 Import Statement" in sidebar

### Step 2: Upload File
1. Click "Choose a file to import"
2. Select your bank statement file (CSV, Excel, or PDF)
3. Wait for file to process

### Step 3: Review Preview
- Check file information (name, size, type)
- Review first 10 rows of data
- Verify column names and data types

### Step 4: Validation
The system automatically checks for:
- Required columns (Date, Description, Amount)
- Data integrity
- Missing values

### Step 5: Process Data
1. Click "🧹 Clean & Process Data" button
2. System will:
   - Remove whitespace
   - Clean column names
   - Remove empty rows
   - Validate data format
3. Review processed data

### Step 6: Import to Database
- Click "💾 Import to Database" (coming soon)
- Transactions will be saved to your FinCo database

## Tips for Best Results

### For CSV/Excel Files
1. ✅ **First row must be headers** - Don't skip the header row
2. ✅ **Use consistent date format** - DD/MM/YYYY or YYYY-MM-DD
3. ✅ **Numbers only for amounts** - Remove ₹ symbols (done automatically)
4. ✅ **Negative for expenses** - Use negative numbers for debits/expenses
5. ✅ **Save as UTF-8** - Use UTF-8 encoding for CSV files

### For PDF Files
1. ✅ **Use tabular statements** - Tables work better than text-only PDFs
2. ✅ **Clean format** - Bank-generated PDFs work best
3. ✅ **First page** - Only first page is processed (for now)
4. ⚠️ **Scanned PDFs** - Image-based PDFs won't work (no OCR support yet)

## Common Issues & Solutions

### Issue: "CSV file is empty"
**Solution**: Check that your file has data and headers

### Issue: "Missing required columns"
**Solution**: 
- Ensure file has Date, Description, Amount columns
- Check column names match (case-insensitive)
- Verify first row contains headers

### Issue: "Error reading Excel"
**Solution**:
- Install openpyxl: `pip install openpyxl`
- Save Excel file as .xlsx format (not .xlsb)

### Issue: "Could not extract tables from PDF"
**Solution**:
- Use PDF with table formatting
- Try exporting to CSV from your bank's portal
- Ensure PDF is not password-protected

### Issue: "UnicodeDecodeError"
**Solution**:
- Save CSV as UTF-8 encoding
- System tries Latin-1 as fallback automatically

## Data Processing

### What Gets Cleaned?

The `clean_and_process_transactions()` function (stub for now) will:

1. **Standardize column names**
   - Convert to lowercase
   - Remove special characters
   - Map alternative names

2. **Parse dates**
   - Detect format automatically
   - Convert to standard format
   - Handle DD/MM/YYYY and YYYY-MM-DD

3. **Clean amounts**
   - Remove currency symbols (₹, $, etc.)
   - Remove commas
   - Convert to float
   - Handle negative values

4. **Remove duplicates**
   - Check for duplicate transactions
   - Based on date + description + amount

5. **Handle missing values**
   - Flag incomplete records
   - Provide default values where appropriate

6. **Auto-categorize** (future)
   - Match merchants to categories
   - Use ML for categorization

7. **Detect transaction type**
   - Income vs Expense
   - Based on amount sign

## Indian Bank Formats

### Common Indian Bank Statement Formats

#### HDFC Bank
```csv
Date,Narration,Chq./Ref.No.,Value Date,Withdrawal Amt.,Deposit Amt.,Closing Balance
21/10/2025,UPI/BigBasket,UPI123456,21/10/2025,2850.00,,49557.50
20/10/2025,Credit Card Bill,CC789012,20/10/2025,12503.00,,52407.50
```

#### ICICI Bank
```csv
Transaction Date,Value Date,Description,Debit,Credit,Balance
21/10/2025,21/10/2025,UPI-BigBasket,2850.00,,49557.50
20/10/2025,20/10/2025,Credit Card,12503.00,,52407.50
```

#### SBI (State Bank of India)
```csv
Txn Date,Value Date,Description,Ref No./Cheque No.,Debit,Credit,Balance
21-Oct-2025,21-Oct-2025,UPI/BigBasket,202510210001,2850.00,,49557.50
20-Oct-2025,20-Oct-2025,CC PAYMENT,202510200001,12503.00,,52407.50
```

#### Axis Bank
```csv
Date,Particulars,Withdrawals,Deposits,Balance
21/10/2025,UPI-BigBasket Groceries,2850.00,,49557.50
20/10/2025,Credit Card Payment,12503.00,,52407.50
```

### Mapping Indian Bank Columns

| Bank | Date Column | Description Column | Amount Columns |
|------|-------------|-------------------|----------------|
| HDFC | Date | Narration | Withdrawal Amt., Deposit Amt. |
| ICICI | Transaction Date | Description | Debit, Credit |
| SBI | Txn Date | Description | Debit, Credit |
| Axis | Date | Particulars | Withdrawals, Deposits |

## API Reference

### Utility Functions (utils.py)

#### `read_csv_file(file)`
Read CSV file and return DataFrame.

**Returns**: `(DataFrame, error_message)`

#### `read_excel_file(file)`
Read Excel file and return DataFrame.

**Returns**: `(DataFrame, error_message)`

#### `read_pdf_file(file)`
Read PDF file and extract tables/text.

**Returns**: `(DataFrame, text_content, error_message)`

#### `validate_transaction_columns(df, required_columns=None)`
Validate DataFrame has required columns.

**Parameters**:
- `df`: DataFrame to validate
- `required_columns`: List of required column names (default: ['date', 'description', 'amount'])

**Returns**: `(is_valid, missing_columns)`

#### `clean_and_process_transactions(df)`
Clean and process imported transaction data (STUB).

**Returns**: Cleaned DataFrame

#### `save_uploaded_file_temp(uploaded_file)`
Save uploaded file to temporary directory.

**Returns**: Path to saved file

## Future Enhancements

### Planned Features

1. **Multi-page PDF support**
   - Process all pages in PDF
   - Combine transactions from multiple pages

2. **Advanced auto-categorization**
   - ML-based merchant categorization
   - Learn from user's past categorizations

3. **Duplicate detection**
   - Smart duplicate checking
   - Fuzzy matching for similar transactions

4. **Bank-specific parsers**
   - Pre-configured parsers for major Indian banks
   - Automatic bank detection

5. **OFX/QFX support**
   - Import Quicken/Intuit formats
   - Direct bank API integration

6. **Transaction mapping**
   - Map columns interactively
   - Save mapping templates

7. **Batch import**
   - Import multiple files at once
   - Merge transactions from different accounts

8. **Import history**
   - Track imported files
   - Prevent re-importing same file

9. **Data validation rules**
   - Custom validation rules
   - Business logic checks

10. **Export processed data**
    - Export to various formats
    - Generate import reports

## Troubleshooting

### Debug Mode

To enable debug logging, set in `.env`:
```env
DEBUG=True
```

### Logging

Check logs for detailed error messages:
```python
# In utils.py, errors are logged
print(f"Error reading CSV: {str(e)}")
```

### Testing

Use the sample CSV feature:
1. Go to Import Statement page
2. Scroll to bottom
3. Click "📥 Download Sample CSV"
4. Test with sample file

## Security Considerations

1. **File Size Limits**
   - Current limit: 16MB (configurable in .env)
   - Prevents memory issues

2. **File Type Validation**
   - Only allowed extensions accepted
   - File content validation

3. **Temporary Files**
   - Saved to system temp directory
   - Automatically cleaned up

4. **Data Privacy**
   - Files processed in-memory when possible
   - No data sent to external servers

## Support

For issues or questions:
- Check this guide first
- Review error messages
- Check console logs (if DEBUG=True)
- Refer to README.md for setup instructions

---

**Version**: 1.0.0  
**Last Updated**: October 21, 2025  
**Author**: FinCo Development Team
