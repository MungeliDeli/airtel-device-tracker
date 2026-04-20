import streamlit as st
from database import get_all_shops, get_all_installers, get_installers_by_shop
import pandas as pd

def show():
    st.title("Airtel Shop Tracker - Admin Dashboard")
    st.caption(f"Logged in as: {st.session_state.get('logged_in_user')}")
    
    tabs = st.tabs(["Global Performance", "Manage Shops & Users"])
    
    with tabs[0]:
        st.header("Global Performance")
        st.info("Here we will show the combined metrics for ALL shops.")
        
        # Placeholder for global data fetch
        st.write("This tab will aggregate Kobo data for all installers across all shops.")
        # In a complete implementation, we would call kobo_api.load_kobo() here
        # and display the global stats exactly like the old Team Performance tab.
        
    with tabs[1]:
        st.header("Shop Management")
        
        shops = get_all_shops()
        if not shops:
            st.warning("No shops found in database. (Ensure MongoDB is connected)")
        else:
            for shop in shops:
                st.subheader(f"Shop: {shop.get('name')}")
                installers = get_installers_by_shop(shop.get('_id'))
                
                if installers:
                    df = pd.DataFrame(installers)
                    st.dataframe(df[["cug_number", "name"]], hide_index=True)
                else:
                    st.write("No installers assigned to this shop.")
                    
            st.divider()
            st.subheader("Add New Installer")
            with st.form("add_installer_form"):
                new_cug = st.text_input("CUG Number")
                new_name = st.text_input("Installer Name")
                # In a real app, populate this selectbox with actual shop IDs/names
                selected_shop = st.selectbox("Assign to Shop", [s.get('name') for s in shops] if shops else [])
                submit = st.form_submit_button("Add Installer")
                
                if submit:
                    st.success(f"Installer {new_name} added to {selected_shop}! (Database write simulated)")
