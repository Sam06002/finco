# FinCo - Personal Finance Tracker

A modern, Streamlit-based personal finance tracker that syncs with Google Sheets. Track income, expenses, and accounts with a sleek dark-mode UI.

**🇮🇳 Localized for Indian Users**

- Currency in Indian Rupees (₹) with lakh/crore formatting
- Designed for Indian banking and financial practices

## Features

- 💰 **Track Income & Expenses** - Add, edit, and delete transactions
- 📊 **Dashboard** - Visual charts showing monthly expense breakdown by category
- 🏦 **Multiple Accounts** - Track across different bank accounts
- 📱 **PWA Support** - Install as a mobile app
- 🌙 **Dark Mode** - Carbon monochrome design
- ☁️ **Google Sheets Sync** - Data stored in your own Google Sheet

## Live Demo

Deployed on Streamlit Cloud: [fincoapp.streamlit.app](https://fincoapp.streamlit.app)

## Quick Start

### Prerequisites

- Python 3.10+
- A Google Cloud service account with Sheets API access
- A Google Sheet shared with the service account

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Sam06002/finco.git
   cd finco
   ```

2. **Create virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google Sheets:**

   Create `.streamlit/secrets.toml`:

   ```toml
   [connections.gsheets]
   spreadsheet = "https://docs.google.com/spreadsheets/d/<your-sheet-id>"
   expenses_worksheet = "Expenses"
   income_worksheet = "Income"
   accounts_worksheet = "Accounts"

   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account@project.iam.gserviceaccount.com"
   client_id = "123456789"
   token_uri = "https://oauth2.googleapis.com/token"
   ```

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## Project Structure

```
finco/
├── app.py              # Main Streamlit application
├── db.py               # Google Sheets data layer with rate limiting
├── requirements.txt    # Python dependencies
├── assets/
│   └── css/style.css   # Carbon monochrome theme
├── static/
│   ├── manifest.json   # PWA manifest
│   └── sw.js           # Service worker
└── docs/               # Documentation
```

## Deployment

See [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) for Streamlit Cloud deployment instructions.

## Google Sheets Structure

Your Google Sheet should have these worksheets:

| Worksheet | Columns                                                        |
| --------- | -------------------------------------------------------------- |
| Expenses  | Date, Description, Amount, Category, Account, Type, Created At |
| Income    | Date, Description, Amount, Category, Account, Type, Created At |
| Accounts  | Name, Balance, Type                                            |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Built With

- [Streamlit](https://streamlit.io/) - Web framework
- [streamlit-gsheets-connection](https://github.com/streamlit/gsheets-connection) - Google Sheets integration
- [Plotly](https://plotly.com/) - Charts and visualizations
