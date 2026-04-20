import streamlit as st
from database import get_supervisors, create_supervisor, add_installer, get_installers_by_supervisor
import pandas as pd

def show(app_mode):
    st.title("Admin Dashboard")
    
    if app_mode == "Global Performance":
        st.header("Global Performance")
        st.info("Here we will show the combined metrics for ALL installers across ALL supervisors.")
        st.write("Placeholder: Kobo Data aggregation will appear here.")
        
    elif app_mode == "Manage Supervisors & Installers":
        st.header("Manage Supervisors & Installers")
        
        supervisors = get_supervisors()
        
        # 1. Summary Table
        st.subheader("Current Supervisors")
        if not supervisors:
            st.warning("No supervisors found in database.")
        else:
            table_data = []
            for sup in supervisors:
                username = sup.get('username')
                shop_name = sup.get('shop_name', 'Unknown')
                installers = get_installers_by_supervisor(username)
                num_installers = len(installers)
                table_data.append({
                    "Supervisor Username": username,
                    "Shop Name": shop_name,
                    "Number of Installers": num_installers
                })
            
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
            
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Add a Supervisor")
            with st.form("add_supervisor_form"):
                new_sup_username = st.text_input("Supervisor Username")
                new_sup_password = st.text_input("Password", type="password")
                new_sup_shop = st.text_input("Shop Name they Supervise")
                submit_sup = st.form_submit_button("Create Supervisor")
                
                if submit_sup:
                    if not new_sup_username or not new_sup_password or not new_sup_shop:
                        st.error("Please fill all fields.")
                    else:
                        success, msg = create_supervisor(new_sup_username, new_sup_password, new_sup_shop)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                            
        with col2:
            st.subheader("Assign an Installer")
            with st.form("add_installer_form"):
                new_cug = st.text_input("Installer CUG Number")
                new_name = st.text_input("Installer Name")
                sup_usernames = [s.get('username') for s in supervisors] if supervisors else []
                selected_sup = st.selectbox("Assign to Supervisor", sup_usernames)
                submit_inst = st.form_submit_button("Add Installer")
                
                if submit_inst:
                    if not new_cug or not new_name or not selected_sup:
                        st.error("Please fill all fields.")
                    else:
                        success, msg = add_installer(new_cug, new_name, selected_sup)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
