import streamlit as st
import pandas as pd
import requests
import re

KOBO_COLS = {
    "cug":   "Installer_Number_CUG",
    "customer": "Customer_Name",
    "phone": "Correct_Customer_Phone_Number",
    "area":  "Area_of_Installation",
    "imei":  "IIMEI_Number",
    "odu":   "ODU_Number",
    "date":  "_submission_time",
}

def resolve_columns(df, needed, label="file"):
    col_lookup = {c.strip().lower(): c for c in df.columns}
    
    def clean_str(s): 
        return re.sub(r'[^a-z0-9]', '', str(s).lower())
        
    clean_lookup = {clean_str(c): c for c in df.columns}

    out_df = pd.DataFrame()

    for key, canonical in needed.items():
        canonical_fuzzy = canonical.strip().lower()
        canonical_clean = clean_str(canonical)
        
        if canonical in df.columns:
            out_df[key] = df[canonical]
        elif canonical_fuzzy in col_lookup:
            out_df[key] = df[col_lookup[canonical_fuzzy]]
        elif canonical_clean in clean_lookup:
            out_df[key] = df[clean_lookup[canonical_clean]]
        else:
            out_df[key] = "Unknown"

    return out_df

@st.cache_data(ttl=600)
def fetch_kobo_data():
    try:
        token = st.secrets["kobo"]["API_TOKEN"]
        form_id = st.secrets["kobo"]["FORM_ID"]
        server_url = st.secrets["kobo"]["SERVER_URL"].rstrip("/")
    except Exception:
        st.error("❌ Kobo credentials not found. Please add them to `.streamlit/secrets.toml`.")
        return None

    if token == "your_api_token_here" or form_id == "your_form_id_here":
        st.error("❌ Please update your `.streamlit/secrets.toml` with real Kobo credentials.")
        return None

    url = f"{server_url}/api/v2/assets/{form_id}/data.json"
    headers = {"Authorization": f"Token {token}"}
    
    try:
        results = []
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            results.extend(data.get("results", []))
            url = data.get("next")
            
        if not results:
            st.warning("⚠️ No data found in the Kobo form.")
            return pd.DataFrame()
            
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"❌ Failed to fetch data from Kobo API: {e}")
        return None

def load_kobo():
    df = fetch_kobo_data()
    if df is None or df.empty:
        return None
        
    df.columns = [c.split('/')[-1] for c in df.columns]
    
    df = resolve_columns(df, KOBO_COLS, label="Kobo API")
    if df is None:
        return None
        
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["imei"] = df["imei"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    df["cug"]  = df["cug"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    return df
