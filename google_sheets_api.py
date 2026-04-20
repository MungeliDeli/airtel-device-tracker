import streamlit as st
import pandas as pd
from kobo_api import resolve_columns

FORM_COLS = {
    "cug":  "Installer CUG",
    "imei": "IMEI Number",
    "date": "Timestamp",
}

@st.cache_data(ttl=600)
def fetch_signout_data(sheet_url=None):
    """Fetches signout data from a public Google Sheet CSV export link."""
    # If no URL provided, try to grab from secrets
    if not sheet_url:
        try:
            sheet_url = st.secrets["google"]["SHEET_CSV_URL"]
        except Exception:
            st.warning("⚠️ Google Sheet URL not provided and not found in secrets.")
            return None
            
    try:
        df = pd.read_csv(sheet_url, dtype=str, on_bad_lines="skip")
        return df
    except Exception as e:
        st.error(f"❌ Failed to fetch data from Google Sheets: {e}")
        return None

def load_signout(sheet_url=None):
    df = fetch_signout_data(sheet_url)
    if df is None or df.empty:
        return None
        
    df = resolve_columns(df, FORM_COLS, label="Sign-out Sheet")
    if df is None:
        return None
        
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["imei"] = df["imei"].astype(str).str.strip()
    df["cug"]  = df["cug"].astype(str).str.strip()
    return df
