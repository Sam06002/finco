# India Localization Guide

## Overview

FinCo has been localized for Indian users with support for Indian currency, number formatting, and financial practices.

## Currency & Number Formatting

### Indian Rupees (₹)
- All currency displays use the Rupee symbol (₹)
- Default currency is set to **INR** (Indian Rupees)

### Indian Number System
We support Indian number formatting with lakhs and crores:
- **International**: 1,234,567.89
- **Indian**: 12,34,567.89

**Examples:**
- ₹1,000 (One thousand)
- ₹1,00,000 (One lakh)
- ₹10,00,000 (Ten lakhs)
- ₹1,00,00,000 (One crore)

### Using Indian Number Format

```python
from utils import format_indian_currency

# Format with Indian numbering system
amount = 1234567.89
formatted = format_indian_currency(amount)
# Output: ₹12,34,567.89
```

## Date Format

### Default: DD/MM/YYYY
Indian users typically use the DD/MM/YYYY format:
- **Indian**: 21/10/2025
- **US**: 10/21/2025

### Available Formats
In settings, users can choose:
1. **DD/MM/YYYY** (Default for India)
2. **MM/DD/YYYY** (US format)
3. **YYYY-MM-DD** (ISO format)

## Time Zone

### Asia/Kolkata (IST)
- Default timezone set to **Asia/Kolkata** (Indian Standard Time)
- UTC+5:30 offset
- No daylight saving time

## Indian Financial Institutions

### Supported Account Types

The application recognizes common Indian account types:

1. **Savings Account** (`savings`)
   - Regular savings bank account
   - Most common account type in India

2. **Current Account** (`current`)
   - Business/commercial account
   - For frequent transactions

3. **Credit Card** (`credit_card`)
   - Credit card accounts
   - Balance shows as negative (owed amount)

4. **Fixed Deposit** (`fixed_deposit`)
   - FD/Term deposit accounts
   - Fixed-term investments

5. **Public Provident Fund** (`ppf`)
   - Government savings scheme
   - Tax-free returns

6. **National Pension System** (`nps`)
   - Retirement savings account
   - Tax benefits under 80C

7. **Recurring Deposit** (`recurring_deposit`)
   - Regular monthly deposits

8. **Demat Account** (`demat`)
   - For holding stocks/securities

### Popular Indian Banks

The system recognizes major Indian banks:

**Public Sector Banks:**
- State Bank of India (SBI)
- Punjab National Bank (PNB)
- Bank of Baroda (BoB)
- Canara Bank
- Bank of India
- Union Bank of India
- Indian Bank

**Private Sector Banks:**
- HDFC Bank
- ICICI Bank
- Axis Bank
- Kotak Mahindra Bank
- IndusInd Bank
- Yes Bank
- IDFC First Bank

**Payment Banks:**
- Paytm Payments Bank
- Airtel Payments Bank
- India Post Payments Bank

## Indian Tax Categories

### Income Tax Considerations

Common categories for Indian users:

**Income Categories:**
- Salary/Wages
- Business Income
- Rental Income
- Capital Gains
- Interest Income (Savings Account, FD, PPF)
- Dividend Income
- Freelance/Professional Income

**Tax-Saving Categories (Section 80C):**
- Life Insurance Premium
- PPF Contribution
- ELSS Investment
- Principal on Home Loan
- Tuition Fees
- NPS Contribution

**Expense Categories:**
- Housing (Rent/EMI)
- Utilities (Electricity, Water, Gas, Internet)
- Transportation (Fuel, Public Transport, Vehicle Maintenance)
- Food & Groceries
- Healthcare (Doctor, Medicines, Insurance)
- Education (School Fees, Tuition, Books)
- Entertainment
- Personal Care
- Clothing
- Mobile/Telecom

## Financial Year

### India's Financial Year: April to March
- **FY 2024-25**: April 1, 2024 to March 31, 2025
- Tax returns (ITR) filed typically by July 31

### Budget Planning
When creating budgets, consider:
- Annual budgets aligned with Financial Year
- Quarterly budgets (Q1: Apr-Jun, Q2: Jul-Sep, Q3: Oct-Dec, Q4: Jan-Mar)
- Monthly budgets

## Payment Methods

### Common in India

1. **UPI (Unified Payments Interface)**
   - PhonePe, Google Pay, Paytm
   - Instant bank-to-bank transfers

2. **NEFT/RTGS/IMPS**
   - Bank transfer methods
   - Different speed and limits

3. **Cash**
   - Still widely used in India

4. **Credit/Debit Cards**
   - RuPay, Visa, Mastercard

5. **Wallets**
   - Paytm, PhonePe, Amazon Pay
   - Prepaid wallets

## GST (Goods and Services Tax)

### Tax Rates
When categorizing expenses, consider GST:
- 0% - Essential goods
- 5% - Essential goods
- 12% - Standard goods
- 18% - Most goods and services
- 28% - Luxury goods

## Investment Instruments

### Popular in India

1. **Fixed Deposits (FD)**
   - Bank fixed deposits
   - Returns: 6-8% p.a.

2. **Public Provident Fund (PPF)**
   - Government savings scheme
   - Lock-in: 15 years
   - Tax-free returns

3. **Mutual Funds**
   - Equity, Debt, Hybrid funds
   - SIP (Systematic Investment Plan)

4. **National Pension System (NPS)**
   - Retirement planning
   - Tax benefits

5. **Stocks & Securities**
   - NSE/BSE listed stocks
   - Traded via demat account

6. **Gold**
   - Physical gold, gold bonds, gold ETFs
   - Traditional investment in India

7. **Real Estate**
   - Property investment
   - Rental income

8. **ELSS (Equity Linked Savings Scheme)**
   - Tax-saving mutual funds
   - 3-year lock-in period

## Localization Settings

### In `.env` file

```env
# Localization Settings (India)
DEFAULT_CURRENCY=INR
DEFAULT_LOCALE=en_IN
DEFAULT_TIMEZONE=Asia/Kolkata
DATE_FORMAT=DD/MM/YYYY
NUMBER_FORMAT=indian  # indian (lakhs/crores) or international
```

## Utility Functions

### Available in `utils.py`

```python
# Format currency in INR
from utils import format_currency
format_currency(1000)  # ₹1,000.00

# Format with Indian number system (lakhs/crores)
from utils import format_indian_currency
format_indian_currency(1234567)  # ₹12,34,567.00

# Parse dates in DD/MM/YYYY format
from utils import parse_date
parse_date("21/10/2025", format="%d/%m/%Y")
```

## Regional Considerations

### Language Support
- **Default**: English (India)
- **Future**: Hindi, Tamil, Telugu, Bengali, etc.
- Unicode support for Indian languages

### Festivals & Holidays
Consider Indian festivals when planning budgets:
- Diwali (October/November) - High spending period
- Holi (March)
- Durga Puja (September/October)
- Christmas
- Eid
- Pongal/Makar Sankranti (January)

### Salary Structure
Common Indian salary components:
- Basic Salary
- HRA (House Rent Allowance)
- Special Allowance
- PF (Provident Fund) - Employee + Employer
- Professional Tax
- TDS (Tax Deducted at Source)

## Best Practices

### For Indian Users

1. **Track Cash Transactions**
   - Cash is still common in India
   - Add "Cash" as an account

2. **Record UPI Payments**
   - Import bank statements
   - Categorize UPI merchant names

3. **Plan for Tax Season**
   - Track 80C investments (up to ₹1.5L)
   - HRA claims
   - Home loan interest

4. **Emergency Fund**
   - Recommended: 6-12 months expenses
   - Keep in liquid accounts (savings, liquid funds)

5. **Festival Budgets**
   - Plan for Diwali, weddings, celebrations
   - Create separate budget categories

6. **Education Planning**
   - Track school/college fees
   - Plan for annual fee increases

7. **Healthcare**
   - Track health insurance premiums
   - Medical expenses for tax deductions

## Data Import

### Bank Statement Formats
Common Indian bank statement formats supported:
- PDF statements (most Indian banks)
- CSV/Excel exports
- SMS/email transaction alerts (future feature)

### Transaction Patterns
Indian transaction descriptions may include:
- UPI/merchant@bank format
- NEFT/RTGS reference numbers
- Card transaction codes

## Future Enhancements

### Planned Features for Indian Users

1. **ITR (Income Tax Return) Export**
   - Generate tax-ready reports
   - 80C, 80D calculation

2. **Bank Integration**
   - Connect to Indian banks via APIs
   - Automatic transaction sync

3. **GST Tracking**
   - For business users
   - Input tax credit management

4. **Multi-language Support**
   - Hindi, regional languages
   - Localized UI

5. **PAN/Aadhaar Integration**
   - Link financial accounts
   - KYC compliance

6. **Investment Tracking**
   - Mutual fund NAV tracking
   - Stock portfolio management
   - SIP calculator

7. **EMI Calculator**
   - Home loan, car loan EMI
   - Prepayment analysis

## Support

For India-specific questions or features:
- Check the main README.md
- Refer to DATABASE_GUIDE.md for data operations
- Contact: support@finco.app (future)

---

**Note**: This application is designed to comply with Indian financial practices and regulations. Always consult with a qualified Chartered Accountant (CA) for tax-related decisions.
