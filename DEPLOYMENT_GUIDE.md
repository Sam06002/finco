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
project_id = "finco-478512"
private_key_id = "7124f8f7a3f48781437d3e6ec6a7e26bc01e85ec"
private_key = """-----BEGIN PRIVATE KEY-----
MIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQC98F1ZvwXycgr6
p0/YXaCj/XDJz+kalvR0ghF/OHFwHLLw89BquPpQh2lKG9L4SGkcTFFCgDxwCjyW
BU2EoQ4eq3B+b5ZiLcxvzxL1A77DTnPG2xYR77IhNjQIQoBNDWfighIjlz8UZAwD
9IGTmBfWGjD8FSRFCfeRNydJsux4zm+J340UAK+H69xOioSn14k0zYTOW7ziSNvv
kpAS5+bl3ZwDkUBQily8511wISF5L/vz27FhmJNkUhzkcYxpeaW+bGVfo3OdN77X
uBTnoff8svOajx90umwsnfm/JRRV+iLBOp1jdQnUxc4vBPSdg8XNuQSvcjs1zvq2
W0/1eXRVAgMBAAECggEAEmAht+AE2ZrHjc5dVCe4CzAmwZotXsGB7uTyf7tchiXQ
o1et2dVW1Nmfib2StdXTjXBOCuqlw4p0qBLlQqfjhNC94Q2Mn/z29/jcSFCkxk0I
YxGpBfKJlNr4l7VPUk+yCuDd6Qw7Mbl9dsMokg3h0yMqNV5vlC+jAC00zirS49uc
h6D8IqL9UnFN5W234QK3kiw6elympomhtLIWTSjm0P/XYeUET3GtgtOWuRagPpDN
nhYutX8w5rREfujBLCKPk+6vq4Jh3U1V5btHJ5J5bWKu/lTiDjBgUEiPFN9NoRQF
v3nfRRN8aqfqM30MJPOne88mBFdMIeRpnFroeuqDFQKBgQD8akFY39wVdrGfcr1r
++nm4NaxRLt5ixIVolpmGLNMJfhASV5Yt0hWyGvIiWx9ttodY3ViOnVLbP2/Y0J9
oelOwF9VI5zlsJ6/mzlw8abW7/Bal2t+1JExiibYlqRxbbhsVKLRgsiZ6yT+0jCi
FcL+EwBJizErvDfaIE5HOh1hywKBgQDAovSGWDiTjJskFAi/MeZscYA6Wj7trmOD
7EwjECKY+h59LuJRio+1ledWbMuL7eZQvVVONdNOZ1ckpcE3k+EasMKH+DfP3yTr
kf3NzAElLIS5yKpm24YdanR2oZNrBjrlYBQBKcPIIR5wt6qTFCnZV3pNeRKDpMxL
00ELrEk+XwJ/Qg+NCrWL5BIsao6dBKXpkYNGrR5P8n9zPDZBcncEdel6D1kkWBOf
2xaZHuLYgg5ZB1gAYLTr/dGIl45i2H6HkRTH3oBzj6mp4nu9jNGx2I7zWMJIX+lC
FrURdZ33a7hLjA6ajjqsRZxFEmvwTntjjRtr99N2Cvw3od7SndGX3wKBgQCoZgvS
4Y5b1h/NU0IuOeYQSMxqtneqebd/HPOV90X3azd6AaFQ3QsyF2BLWgI6Sfb7//dx
znXxZT91xvz4o+q11W3JRUEtFAoHcPFplXwuzhMdAgGMtz0vu98h0a+4cJLN78at
GaCP8/vTV4vi1U6cM++ziDKaKFd7tap4FN1WiwKBgGw/veBCn1o1jclWtG6k2uGx
/oxWxTIJxdifmhYYb3yHN0tqM/gSG5iiuIc+Mx9hlnWKN29LSlAcQxddvPnh7TIq
fI8QR/KNOILvgfk07m2FatkD1zj8RO2ESGtCnfvixQyrX0BDz7n1NhJ86xnh4WIH
cHa/GiJq8SrQfwmxXShi
-----END PRIVATE KEY-----"""
client_email = "expense-tracker-sa@finco-478512.iam.gserviceaccount.com"
client_id = "111974447906012094144"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/expense-tracker-sa%40finco-478512.iam.gserviceaccount.com"
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
