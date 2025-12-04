# FinCo Application Structure

## Overview

The FinCo Streamlit application is organized into multiple pages with a sidebar navigation system. The application follows a clean, modular architecture that makes it easy to expand functionality in the future.

## File Structure

```
finco/
├── app.py                   # Main Streamlit application (THIS FILE)
├── models.py                # Database ORM models
├── db.py                    # Database connection and session management
├── utils.py                 # Utility functions
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not tracked)
├── assets/
│   ├── icons/              # App icons and logos
│   │   └── logo.png        # Place logo here (optional)
│   ├── images/             # General images
│   └── css/                # Custom stylesheets
└── *.md                     # Documentation files
```

## Application Architecture

### 1. Configuration (Lines 1-64)
- Module imports
- Environment variable loading
- Page configuration (`st.set_page_config`)
- Session state initialization

### 2. Sidebar Navigation (Lines 66-142)
- `render_sidebar()` function
- Logo display (if present at `assets/icons/logo.png`)
- Navigation menu with 7 pages
- Footer with version info

### 3. Page Functions (Lines 144-438)

Each page is implemented as a standalone function:

#### **show_dashboard()** (Lines 150-243)
- **Status**: ✅ Functional with sample data
- **Features**: 
  - Financial summary cards (Net Worth, Income, Expenses, Savings Rate)
  - Income vs Expenses chart
  - Placeholder for future features
- **TODO**: Connect to real database data

#### **show_transactions()** (Lines 245-281)
- **Status**: 🚧 Stub/Placeholder
- **Planned Features**:
  - Add transaction form
  - Transaction list with filters
  - Edit/delete capabilities
  - Export to CSV
  - Bulk operations

#### **show_budgets()** (Lines 283-308)
- **Status**: 🚧 Stub/Placeholder
- **Planned Features**:
  - Create budgets by category
  - Track spending vs budget
  - Visual progress bars
  - Budget alerts

#### **show_goals()** (Lines 310-335)
- **Status**: 🚧 Stub/Placeholder
- **Planned Features**:
  - Set financial goals
  - Track progress
  - Link to accounts
  - Milestone tracking

#### **show_investments()** (Lines 337-362)
- **Status**: 🚧 Stub/Placeholder
- **Planned Features**:
  - Track investments
  - Portfolio performance
  - Returns calculation
  - Asset allocation

#### **show_import()** (Lines 364-399)
- **Status**: 🚧 Stub/Placeholder
- **Planned Features**:
  - PDF/CSV statement upload
  - Automatic parsing
  - Transaction categorization
  - Duplicate detection

#### **show_settings()** (Lines 401-438)
- **Status**: 🚧 Stub/Placeholder
- **Planned Features**:
  - Profile management
  - Password change
  - Preferences (currency, locale)
  - Data export/backup

### 4. Main Application (Lines 440-498)

#### **main()** function
- Initializes database (`init_db()`)
- Renders sidebar navigation
- Routes to appropriate page based on `st.session_state.page`
- Error handling for database initialization

#### Page Routing Logic
```python
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
elif page == 'import':
    show_import()
elif page == 'settings':
    show_settings()
else:
    show_dashboard()  # Default fallback
```

## Navigation Menu

The sidebar navigation includes:

| Icon | Page | Key | Status |
|------|------|-----|--------|
| 📊 | Dashboard | `dashboard` | ✅ Functional |
| 💸 | Transactions | `transactions` | 🚧 Stub |
| 🎯 | Budgets | `budgets` | 🚧 Stub |
| 🏆 | Goals | `goals` | 🚧 Stub |
| 📈 | Investments | `investments` | 🚧 Stub |
| 📄 | Import Statement | `import` | 🚧 Stub |
| ⚙️ | Settings | `settings` | 🚧 Stub |

## Session State Variables

The application uses Streamlit's session state to maintain user context:

```python
st.session_state.page            # Current page ('dashboard', 'transactions', etc.)
st.session_state.user_id          # User ID (for future authentication)
st.session_state.authenticated    # Authentication status (for future use)
```

## How to Expand Functionality

### Adding Features to Existing Pages

1. **Locate the page function** in `app.py` (e.g., `show_transactions()`)
2. **Replace the stub content** with actual implementation
3. **Use database sessions** from `db.py`:
   ```python
   from db import DatabaseSession
   
   with DatabaseSession() as db:
       # Your database operations
       transactions = db.query(Transaction).all()
   ```
4. **Add forms and widgets** using Streamlit components
5. **Update the TODO comments** to track progress

### Adding a New Page

1. **Create a new page function** following the naming convention:
   ```python
   def show_new_page():
       """
       New Page - Description
       
       TODO: Implement features
       """
       st.title("🔹 New Page")
       st.header("New Page – Coming Soon!")
   ```

2. **Add to navigation menu** in `render_sidebar()`:
   ```python
   menu_items = [
       # ... existing items ...
       ("New Page", "new_page", "🔹"),
   ]
   ```

3. **Add route in main()** function:
   ```python
   elif page == 'new_page':
       show_new_page()
   ```

## Code Comments

The codebase includes extensive comments:

- **Section headers** with `=======` dividers for major sections
- **Subsection headers** with `-------` dividers
- **Inline comments** explaining complex logic
- **Docstrings** for all functions with TODO lists
- **Usage examples** in function documentation

## Best Practices

When expanding functionality:

1. **Follow the existing code style** (comments, structure, naming)
2. **Use session state** for cross-page data sharing
3. **Implement error handling** with try/except blocks
4. **Add user feedback** with `st.success()`, `st.error()`, etc.
5. **Keep functions focused** - one page per function
6. **Document as you go** - update docstrings and TODOs
7. **Test incrementally** - verify each feature before moving on

## Running the Application

```bash
# Initialize database (first time only)
python init_database.py

# Start the Streamlit app
streamlit run app.py

# Access at http://localhost:8501
```

## Next Steps

1. **Implement Transaction Management** (highest priority)
   - CRUD operations for transactions
   - Filter and search functionality
   - Database integration

2. **Add Authentication** (if multi-user support needed)
   - User login/registration
   - Session management
   - Password hashing with bcrypt

3. **Connect Dashboard to Database**
   - Query real transaction data
   - Calculate actual metrics
   - Display recent activity

4. **Implement Budget Tracking**
   - Budget CRUD operations
   - Spending calculations
   - Progress visualization

5. **Build Import Functionality**
   - PDF parsing with pdfplumber
   - CSV import
   - Transaction categorization

## Support

For questions or issues, refer to:
- `README.md` - Project overview and setup
- `DATABASE_GUIDE.md` - Database operations
- `INSTALLATION.md` - Detailed installation guide
