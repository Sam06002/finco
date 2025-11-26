"""Google Sheets data layer for FinCo using streamlit-gsheets-connection."""

from __future__ import annotations

from typing import Dict

import pandas as pd
import streamlit as st
from gspread.exceptions import WorksheetNotFound
from streamlit_gsheets import GSheetsConnection
from streamlit_gsheets.gsheets_connection import GSheetsServiceAccountClient

_CONFIG = (
    st.secrets.get("gsheets")
    or st.secrets.get("connections", {}).get("gsheets")
    or {}
)
EXPENSES_WORKSHEET = _CONFIG.get("expenses_worksheet", "Expenses")
INCOME_WORKSHEET = _CONFIG.get("income_worksheet", "Income")
ACCOUNTS_WORKSHEET = _CONFIG.get("accounts_worksheet", "Accounts")


def _get_spreadsheet_identifier() -> str:
    # Check session state first for user overrides
    if "spreadsheet_url" in st.session_state:
        return st.session_state["spreadsheet_url"]

    for key in ("spreadsheet", "spreadsheet_url"):
        value = _CONFIG.get(key)
        if value:
            return value
    raise RuntimeError(
        "Missing Google Sheets configuration. "
        "Please set 'spreadsheet' (or 'spreadsheet_url') inside [gsheets] secrets."
    )


class CustomGSheetsConnection(GSheetsConnection):
    """Custom connection to allow dynamic credential passing."""
    
    def _connect(self, **kwargs):
        if "service_account_info" in kwargs:
            return GSheetsServiceAccountClient(kwargs["service_account_info"])
        return super()._connect()


def get_connection() -> GSheetsConnection:
    """Return a Google Sheets connection, using user credentials if available."""
    if "google_credentials" in st.session_state:
        return st.connection(
            "gsheets_user",
            type=CustomGSheetsConnection,
            service_account_info=st.session_state["google_credentials"],
        )
    return st.connection("gsheets", type=GSheetsConnection)


def _read_sheet(worksheet: str, *, required: bool = True) -> pd.DataFrame:
    try:
        df = get_connection().read(
            spreadsheet=_get_spreadsheet_identifier(),
            worksheet=worksheet,
        )
    except WorksheetNotFound as exc:
        if not required:
            return pd.DataFrame()
        raise RuntimeError(f"Worksheet '{worksheet}' not found.") from exc
    except Exception as exc:  # pragma: no cover - Streamlit helper raises runtime errors
        raise RuntimeError(f"Unable to read '{worksheet}' worksheet: {exc}") from exc

    if df is None:
        return pd.DataFrame()
    return df.fillna("")


def _write_sheet(worksheet: str, data: pd.DataFrame) -> None:
    try:
        get_connection().update(
            spreadsheet=_get_spreadsheet_identifier(),
            worksheet=worksheet,
            data=data,
        )
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Unable to write to '{worksheet}' worksheet: {exc}") from exc


def _append_row(worksheet: str, row: Dict) -> pd.DataFrame:
    df = _read_sheet(worksheet)
    updated = pd.concat([df, pd.DataFrame([row])], ignore_index=True) if not df.empty else pd.DataFrame([row])
    _write_sheet(worksheet, updated)
    return updated


def get_expenses_df() -> pd.DataFrame:
    return _read_sheet(EXPENSES_WORKSHEET)


def get_income_df() -> pd.DataFrame:
    return _read_sheet(INCOME_WORKSHEET)


def get_accounts_df() -> pd.DataFrame:
    return _read_sheet(ACCOUNTS_WORKSHEET, required=False)


def add_expense_row(data: Dict) -> pd.DataFrame:
    return _append_row(EXPENSES_WORKSHEET, data)


def add_income_row(data: Dict) -> pd.DataFrame:
    return _append_row(INCOME_WORKSHEET, data)
