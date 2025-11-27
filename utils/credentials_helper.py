"""Helper functions for Google Sheets credentials management."""

import json
import streamlit as st
from typing import Dict, Optional, Tuple


def validate_json_credentials(json_str: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Validate Google Service Account JSON credentials.
    
    Args:
        json_str: JSON string containing service account credentials
        
    Returns:
        Tuple of (is_valid, credentials_dict, error_message)
    """
    try:
        credentials = json.loads(json_str)
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON format: {str(e)}"
    
    # Check for required fields
    required_fields = [
        'type',
        'project_id',
        'private_key_id',
        'private_key',
        'client_email',
        'client_id',
        'auth_uri',
        'token_uri'
    ]
    
    missing_fields = [field for field in required_fields if field not in credentials]
    
    if missing_fields:
        return False, None, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Validate it's a service account
    if credentials.get('type') != 'service_account':
        return False, None, "Credentials must be for a service account"
    
    return True, credentials, ""


def extract_service_account_email(credentials: Dict) -> str:
    """
    Extract service account email from credentials.
    
    Args:
        credentials: Service account credentials dictionary
        
    Returns:
        Service account email address
    """
    return credentials.get('client_email', 'unknown@unknown.com')


def test_google_sheets_connection(
    credentials: Dict,
    spreadsheet_url: str,
    worksheet_name: str = "Sheet1"
) -> Tuple[bool, str]:
    """
    Test if Google Sheets connection works with provided credentials.
    
    Args:
        credentials: Service account credentials dictionary
        spreadsheet_url: Full URL or ID of the Google Sheet
        worksheet_name: Name of worksheet to test (default: Sheet1)
        
    Returns:
        Tuple of (success, message)
    """
    try:
        from streamlit_gsheets import GSheetsConnection
        import pandas as pd
        
        # Store credentials temporarily in session state
        old_creds = st.session_state.get('test_credentials')
        old_url = st.session_state.get('test_spreadsheet_url')
        
        st.session_state['test_credentials'] = credentials
        st.session_state['test_spreadsheet_url'] = spreadsheet_url
        
        # Try to create connection and read a worksheet
        try:
            conn = st.connection("test_gsheets", type=GSheetsConnection)
            
            # Try to read the worksheet
            df = conn.read(
                spreadsheet=spreadsheet_url,
                worksheet=worksheet_name,
                ttl=0  # No caching for test
            )
            
            # Clean up test credentials
            if old_creds:
                st.session_state['test_credentials'] = old_creds
            else:
                st.session_state.pop('test_credentials', None)
                
            if old_url:
                st.session_state['test_spreadsheet_url'] = old_url
            else:
                st.session_state.pop('test_spreadsheet_url', None)
            
            return True, f"✅ Successfully connected! Found worksheet '{worksheet_name}' with {len(df)} rows."
            
        except Exception as e:
            # Clean up test credentials
            st.session_state.pop('test_credentials', None)
            st.session_state.pop('test_spreadsheet_url', None)
            
            error_msg = str(e)
            if "not found" in error_msg.lower():
                return False, f"❌ Worksheet '{worksheet_name}' not found. Please check the worksheet name."
            elif "permission" in error_msg.lower() or "forbidden" in error_msg.lower():
                return False, f"❌ Permission denied. Make sure you've shared the Google Sheet with: {extract_service_account_email(credentials)}"
            else:
                return False, f"❌ Connection failed: {error_msg}"
                
    except ImportError:
        return False, "❌ Required package 'streamlit-gsheets-connection' not installed"
    except Exception as e:
        return False, f"❌ Unexpected error: {str(e)}"


def setup_google_sheets_credentials(
    credentials: Dict,
    spreadsheet_url: str,
    expenses_worksheet: str = "Expenses",
    income_worksheet: str = "Income",
    accounts_worksheet: str = "Accounts"
) -> bool:
    """
    Store Google Sheets credentials and configuration in session state.
    
    Args:
        credentials: Service account credentials dictionary
        spreadsheet_url: Full URL or ID of the Google Sheet
        expenses_worksheet: Name of expenses worksheet
        income_worksheet: Name of income worksheet
        accounts_worksheet: Name of accounts worksheet
        
    Returns:
        True if successful
    """
    try:
        # Store in session state
        st.session_state['gsheets_credentials'] = credentials
        st.session_state['spreadsheet_url'] = spreadsheet_url
        st.session_state['expenses_worksheet'] = expenses_worksheet
        st.session_state['income_worksheet'] = income_worksheet
        st.session_state['accounts_worksheet'] = accounts_worksheet
        st.session_state['credentials_configured'] = True
        
        return True
    except Exception:
        return False


def clear_credentials():
    """Clear all Google Sheets credentials from session state."""
    keys_to_remove = [
        'gsheets_credentials',
        'spreadsheet_url',
        'expenses_worksheet',
        'income_worksheet',
        'accounts_worksheet',
        'credentials_configured'
    ]
    
    for key in keys_to_remove:
        st.session_state.pop(key, None)


def is_credentials_configured() -> bool:
    """Check if Google Sheets credentials are configured."""
    return st.session_state.get('credentials_configured', False)
