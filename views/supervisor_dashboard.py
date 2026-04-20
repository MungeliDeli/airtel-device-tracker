import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from kobo_api import load_kobo
from google_sheets_api import load_signout
from database import get_installers_by_supervisor

def show(app_mode):
    st.title("Supervisor Dashboard")
    
    username = st.session_state.get('logged_in_user')
    shop_name = st.session_state.get('shop_name', 'Unknown Shop')
    
    # 1. Get the installers specifically assigned to this supervisor
    installers_docs = get_installers_by_supervisor(username)
    if not installers_docs:
        st.warning("⚠️ No installers are assigned to you yet.")
        st.stop()
        
    # Create a dictionary of {cug_number: name} for easy mapping
    my_team = {doc.get("cug_number"): doc.get("name") for doc in installers_docs}
    
    st.caption(f"Shop: {shop_name} | Managing {len(my_team)} installers.")

    if app_mode == "Team Performance":
        st.header("Your Team's Performance")
        with st.spinner("Fetching data from KoboToolbox..."):
            kobo = load_kobo()
            
        if kobo is None:
            st.stop()
            
        # CRITICAL RBAC STEP: Filter Kobo data so it ONLY contains CUGs belonging to this supervisor
        my_kobo_data = kobo[kobo["cug"].isin(my_team.keys())].copy()
        my_kobo_data["Installer Name"] = my_kobo_data["cug"].map(my_team)
        
        if my_kobo_data.empty:
            st.info("No installations found for your team members yet.")
        else:
            st.success(f"Found {len(my_kobo_data)} total installations for your team!")
            # The rest of the performance metrics logic from the original app goes here...
            st.dataframe(my_kobo_data[["Installer Name", "cug", "imei", "date"]].head(10), hide_index=True)

    elif app_mode == "Device Reconciliation":
        st.header("Device Reconciliation")
        st.info("Reading sign-out data directly from Google Sheets...")
        
        with st.spinner("Fetching Sign-out data..."):
            signout = load_signout()
            
        if signout is not None:
            # CRITICAL RBAC STEP: Filter sign-out data for this supervisor's team only
            my_signouts = signout[signout["cug"].isin(my_team.keys())].copy()
            st.success(f"Loaded {len(my_signouts)} sign-out records for your team.")
            
            # The rest of the reconciliation logic from the original app goes here...
            st.dataframe(my_signouts.head(10), hide_index=True)
