# FinCo Deployment Guide - Streamlit Cloud

This guide will help you deploy FinCo to Streamlit Community Cloud with secure credential management.

## Prerequisites

- A GitHub account
- Your FinCo repository pushed to GitHub
- A Google Cloud service account with access to your Google Sheets
- Your Google Sheets spreadsheet URL

## Deployment Steps

### 1. Push Your Code to GitHub

Make sure your latest code is pushed to the `main` branch:

```bash
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click "New app"
3. Select your repository: `Sam06002/finco`
4. Choose branch: `main`
5. Main file path: `app.py`
6. Click "Deploy"

### 3. Configure Secrets

Once your app is deployed:

1. Go to your app's dashboard on Streamlit Cloud
2. Click the hamburger menu (⋮) → "Settings"
3. Navigate to the "Secrets" section
4. Paste the following configuration (replace with your actual values):

```toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
expenses_worksheet = "Expenses"
income_worksheet = "Income"
accounts_worksheet = "Accounts"

# Google Service Account Credentials
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
...your private key content...
-----END PRIVATE KEY-----"""
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account"
universe_domain = "googleapis.com"
```

> [!IMPORTANT]
> Make sure to replace the `spreadsheet` URL with your actual Google Sheets URL!

5. Click "Save"
6. Your app will automatically restart with the new configuration

### 4. Verify Deployment

1. Wait for the app to restart (usually takes 30-60 seconds)
2. Visit your app URL
3. You should see the dashboard with your Google Sheets data
4. Try adding an expense to verify the connection works

## Local Development

For local development, create a `.streamlit/secrets.toml` file in your project directory with the same configuration as above. This file is already in `.gitignore` so it won't be committed to your repository.

## Troubleshooting

### "Missing Google Sheets configuration" Error

This means the secrets weren't configured properly. Double-check:

- The secrets are in the correct TOML format
- There are no syntax errors in the secrets
- The app has been restarted after adding secrets

### "Worksheet not found" Error

Make sure your Google Sheets has the following worksheets:

- `Expenses`
- `Income`
- `Accounts`

The worksheet names are case-sensitive!

### Permission Denied Error

Ensure your service account email (`expense-tracker-sa@finco-478512.iam.gserviceaccount.com`) has been granted **Editor** access to your Google Sheet:

1. Open your Google Sheet
2. Click "Share"
3. Add the service account email
4. Set permission to "Editor"
5. Click "Send"

## Security Notes

✅ **Your credentials are secure** - They're stored in Streamlit's encrypted secrets management system
✅ **Not in your repository** - The credentials never touch your Git repository
✅ **Private to your app** - Only your deployed app can access these secrets

## Next Steps

- Customize your expense categories
- Add more worksheets as needed
- Invite team members to collaborate on your Google Sheet
