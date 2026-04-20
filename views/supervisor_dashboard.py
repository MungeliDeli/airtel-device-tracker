import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from kobo_api import load_kobo
from google_sheets_api import load_signout
from database import get_installers_by_shop

def show():
    st.title("Airtel Shop Tracker - Supervisor Dashboard")
    
    shop_id = st.session_state.get('shop_id')
    
    # 1. Get the installers specifically for this shop
    installers_docs = get_installers_by_shop(shop_id)
    if not installers_docs:
        st.warning("⚠️ No installers are assigned to your shop in the database.")
        st.stop()
        
    # Create a dictionary of {cug_number: name} for easy mapping
    my_team = {doc.get("cug_number"): doc.get("name") for doc in installers_docs}
    
    st.caption(f"Welcome, Supervisor {st.session_state.get('logged_in_user')}! Managing {len(my_team)} installers.")

    tabs = st.tabs(["Team Performance", "Device Reconciliation"])
    
    with tabs[0]:
        st.header("Your Team's Performance")
        with st.spinner("Fetching data from KoboToolbox..."):
            kobo = load_kobo()
            
        if kobo is None:
            st.stop()
            
        # CRITICAL RBAC STEP: Filter Kobo data so it ONLY contains CUGs belonging to this shop
        my_kobo_data = kobo[kobo["cug"].isin(my_team.keys())].copy()
        my_kobo_data["Installer Name"] = my_kobo_data["cug"].map(my_team)
        
        if my_kobo_data.empty:
            st.info("No installations found for your team members yet.")
        else:
            st.success(f"Found {len(my_kobo_data)} total installations for your team!")
            # The rest of the performance metrics logic from the original app goes here...
            st.dataframe(my_kobo_data[["Installer Name", "cug", "imei", "date"]].head(10), hide_index=True)

    with tabs[1]:
        st.header("Device Reconciliation")
        st.info("Reading sign-out data directly from Google Sheets...")
        
        with st.spinner("Fetching Sign-out data..."):
            signout = load_signout()
            
        if signout is not None:
            # CRITICAL RBAC STEP: Filter sign-out data for this shop only
            my_signouts = signout[signout["cug"].isin(my_team.keys())].copy()
            st.success(f"Loaded {len(my_signouts)} sign-out records for your team.")
            
            # The rest of the reconciliation logic from the original app goes here...
            st.dataframe(my_signouts.head(10), hide_index=True)
