# FinCo - Personal Finance Tracker (Google Sheets Edition)

FinCo is a modern, Streamlit-based personal finance application that stores data in Google Sheets. Track income, expenses, and accounts with a simple, fast UI.

**🇮🇳 Localized for Indian Users**
- Currency in Indian Rupees (₹)
- Indian number formatting (lakhs & crores)
- DD/MM/YYYY date format
- Designed for Indian banking and financial practices

## Features

- 💰 Track income and expenses
- 🏦 Manage multiple accounts
- 📊 View financial reports and analytics
- 📅 Set and track budgets
- 📱 Responsive web interface
- 🔄 SQLite database for data persistence

## Prerequisites

- Python 3.10+
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd finco
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure Google Sheets (required):
   - Create a file at `.streamlit/secrets.toml` with your Google Sheets settings. This file is ignored by Git.
   - Example `secrets.toml`:
     ```toml
     [gsheets]
     # Use the full Google Sheets URL or spreadsheet ID
     spreadsheet = "https://docs.google.com/spreadsheets/d/<your-id>"
     expenses_worksheet = "Expenses"
     income_worksheet   = "Income"
     accounts_worksheet = "Accounts"

     # Paste the service account JSON fields below (keys shown are examples):
     type = "service_account"
     project_id = "..."
     private_key_id = "..."
     private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
     client_email = "...@...gserviceaccount.com"
     client_id = "..."
     token_uri = "https://oauth2.googleapis.com/token"
     ```
   - Alternatively, you can use the `[connections.gsheets]` block supported by Streamlit. The app reads either `[gsheets]` or `[connections.gsheets]` (see `db.py`).
   - Share the target Google Sheet with the service account email (Editor access).

5. Keep credentials out of Git:
   - `.streamlit/secrets.toml` and `google-credentials.json` are ignored via `.gitignore`.
   - If you ever accidentally staged `google-credentials.json`, remove it from Git with:
     ```bash
     git rm --cached google-credentials.json
     ```

4. Set up environment variables:
   - The `.env` file is already configured with default values
   - Update the `DATABASE_URL` in `.env` if you want to use a different database location
   - For PostgreSQL: `DATABASE_URL=postgresql://username:password@localhost/finco`
   - For MySQL: `DATABASE_URL=mysql://username:password@localhost/finco`

5. Initialize the database:
   ```bash
   python init_database.py
   ```
   
   This will:
   - Create all necessary database tables
   - Optionally populate the database with sample data for testing

## Running the Application

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to `http://localhost:8501`

## Commit and Push Safely

Before committing, verify that sensitive files are ignored:

```bash
git status
git ls-files -- google-credentials.json  # should output nothing
```

Commit your changes:

```bash
git add .
git commit -m "feat: Google Sheets setup and docs"
git push origin main
```

## Database Management

### Initialize Database
```bash
python init_database.py
```

### Accessing the Database Session
The application provides three ways to access database sessions:

1. **Generator Pattern** (for FastAPI-style dependencies):
   ```python
   from db import get_db
   
   for db in get_db():
       user = db.query(User).first()
   ```

2. **Direct Session** (manual close required):
   ```python
   from db import get_db_session
   
   db = get_db_session()
   try:
       user = db.query(User).first()
   finally:
       db.close()
   ```

3. **Context Manager** (automatic commit/rollback):
   ```python
   from db import DatabaseSession
   
   with DatabaseSession() as db:
       user = User(username="john", email="john@example.com")
       db.add(user)
       # Automatically commits on successful exit
   ```

## Project Structure

```
finco/
├── app.py              # Main Streamlit application
├── models.py           # Database models (SQLAlchemy ORM)
├── db.py               # Database connection and session management
├── utils.py            # Utility functions
├── init_database.py    # Database initialization script
├── requirements.txt    # Project dependencies
├── .env                # Environment variables
├── README.md           # This file
└── finco.db            # SQLite database (created after initialization)
```

## Database

The application uses SQLite by default (stored in `finco.db`). You can change the database URL in the `.env` file to use a different database.

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Icons from [Bootstrap Icons](https://icons.getbootstrap.com/)
