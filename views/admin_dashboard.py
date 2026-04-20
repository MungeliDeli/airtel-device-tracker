import streamlit as st
from database import (
    get_supervisors, create_supervisor, remove_supervisor,
    add_installer, get_installers_by_supervisor, remove_installer,
    sync_installations_to_mongo, get_all_installations, get_all_installers
)
import pandas as pd
from datetime import datetime, timedelta
from kobo_api import load_kobo


def validate_cug(cug: str):
    """Validates a CUG number. Must be exactly 9 digits and start with 97898."""
    if not cug.isdigit():
        return False, "CUG must contain digits only."
    if len(cug) != 9:
        return False, f"CUG must be exactly 9 digits (you entered {len(cug)})."
    if not cug.startswith("97898"):
        return False, "CUG must start with **97898**."
    return True, ""


def show(app_mode):
    st.title("Admin Dashboard")

    if app_mode == "Global Performance":
        st.header("Global Performance")
        
        # ── 1. Sync Button ──
        col1, col2 = st.columns([3, 1])
        col1.info("Combined metrics for ALL installers across ALL supervisors.")
        if col2.button("🔄 Sync Latest Data from Kobo", use_container_width=True):
            with st.spinner("Fetching from Kobo..."):
                kobo_df = load_kobo()
                if kobo_df is not None and not kobo_df.empty:
                    success, msg = sync_installations_to_mongo(kobo_df)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("No data returned from Kobo API.")
        
        st.divider()
        
        # ── 2. Load Data ──
        installations = get_all_installations()
        if not installations:
            st.warning("No installations found in the database. Please sync data from Kobo.")
        else:
            df_inst = pd.DataFrame(installations)
            
            # Ensure date is datetime
            df_inst['date'] = pd.to_datetime(df_inst['date'], errors='coerce')
            
            # Get all installers to map cug -> supervisor and name
            all_installers = get_all_installers()
            installer_map = {inst.get("cug_number"): inst for inst in all_installers}
            
            def get_installer_name(cug):
                return installer_map.get(cug, {}).get("name", "Unknown")
                
            def get_supervisor(cug):
                return installer_map.get(cug, {}).get("supervisor_username", "Unassigned")
                
            df_inst["Installer Name"] = df_inst["cug"].apply(get_installer_name)
            df_inst["Supervisor"] = df_inst["cug"].apply(get_supervisor)
            
            # ── 3. Top Level Metrics ──
            today_dt = datetime.today()
            start_of_week = today_dt - timedelta(days=today_dt.weekday())
            start_of_month = today_dt.replace(day=1)
            
            t_all = len(df_inst)
            t_today = len(df_inst[df_inst['date'].dt.date == today_dt.date()])
            t_week = len(df_inst[df_inst['date'] >= start_of_week])
            t_month = len(df_inst[df_inst['date'] >= start_of_month])
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Today's Total", t_today)
            c2.metric("This Week's Total", t_week)
            c3.metric("This Month's Total", t_month)
            c4.metric("All Time Total", t_all)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # ── 4. Tables ──
            tab1, tab2 = st.tabs(["Supervisor Performance", "Installer Performance"])
            
            with tab1:
                st.subheader("Installations per Supervisor")
                sup_perf = df_inst.groupby("Supervisor").size().reset_index(name="Total Installations")
                sup_perf = sup_perf.sort_values("Total Installations", ascending=False)
                st.dataframe(sup_perf, use_container_width=True, hide_index=True)
                
            with tab2:
                st.subheader("Installations per Installer")
                inst_perf = df_inst.groupby(["Installer Name", "cug", "Supervisor"]).size().reset_index(name="Total Installations")
                inst_perf = inst_perf.rename(columns={"cug": "CUG Number"})
                inst_perf = inst_perf.sort_values("Total Installations", ascending=False)
                st.dataframe(inst_perf, use_container_width=True, hide_index=True)

    elif app_mode == "Manage Supervisors & Installers":
        st.header("Manage Supervisors & Installers")

        supervisors = get_supervisors()

        # Initialise confirm-delete states
        if "confirm_delete_sup" not in st.session_state:
            st.session_state.confirm_delete_sup = None
        if "confirm_delete_cug" not in st.session_state:
            st.session_state.confirm_delete_cug = None

        # ── 1. Supervisors Table with Remove ─────────────────────────────────
        st.subheader("Current Supervisors")
        if not supervisors:
            st.warning("No supervisors found in database yet.")
        else:
            # Table header
            hcols = st.columns([3, 3, 2, 1])
            hcols[0].markdown("**Supervisor Username**")
            hcols[1].markdown("**Shop Name**")
            hcols[2].markdown("**No. of Installers**")
            hcols[3].markdown("**Remove**")

            for sup in supervisors:
                username  = sup.get("username")
                shop_name = sup.get("shop_name", "Unknown")
                count     = len(get_installers_by_supervisor(username))

                row = st.columns([3, 3, 2, 1])
                row[0].write(username)
                row[1].write(shop_name)
                row[2].write(count)

                # Confirm state for this supervisor
                if st.session_state.confirm_delete_sup == username:
                    confirm_cols = st.columns([1, 1, 4])
                    if confirm_cols[0].button("Yes, remove", key=f"yes_sup_{username}", type="primary"):
                        success, msg = remove_supervisor(username)
                        if success:
                            st.success(f"✅ Supervisor **{username}** and all their installers have been removed.")
                        else:
                            st.error(f"❌ {msg}")
                        st.session_state.confirm_delete_sup = None
                        st.rerun()
                    if confirm_cols[1].button("Cancel", key=f"cancel_sup_{username}"):
                        st.session_state.confirm_delete_sup = None
                        st.rerun()
                    confirm_cols[2].warning(
                        f"⚠️ This will permanently remove **{username}** "
                        f"and all **{count}** installer(s) under them. This cannot be undone."
                    )
                else:
                    if row[3].button("🗑️", key=f"del_sup_{username}", help=f"Remove {username}"):
                        st.session_state.confirm_delete_sup = username
                        st.rerun()

        # ── 2. Installer Drill-Down ───────────────────────────────────────────
        st.divider()
        st.subheader("Installer Drill-Down")

        if not supervisors:
            st.info("Create a supervisor first to see their installers here.")
        else:
            sup_map = {s.get("username"): s.get("shop_name", "Unknown") for s in supervisors}
            selected_sup = st.selectbox(
                "Select a Supervisor to view their installers",
                list(sup_map.keys()),
                format_func=lambda u: f"{u}  —  {sup_map[u]}"
            )

            if selected_sup:
                installers = get_installers_by_supervisor(selected_sup)

                if not installers:
                    st.info(f"No installers assigned to **{selected_sup}** yet.")
                else:
                    st.markdown(f"**{len(installers)} installer(s) under {selected_sup}**")

                    # Table header
                    hcols2 = st.columns([4, 3, 1])
                    hcols2[0].markdown("**Installer Name**")
                    hcols2[1].markdown("**CUG Number**")
                    hcols2[2].markdown("**Remove**")

                    for inst in installers:
                        cug  = inst.get("cug_number")
                        name = inst.get("name")

                        row_cols = st.columns([4, 3, 1])
                        row_cols[0].write(name)
                        row_cols[1].write(cug)

                        if st.session_state.confirm_delete_cug == cug:
                            confirm_cols = st.columns([1, 1, 4])
                            if confirm_cols[0].button("Yes, remove", key=f"yes_inst_{cug}", type="primary"):
                                success, msg = remove_installer(cug)
                                if success:
                                    st.success(f"✅ **{name}** has been removed.")
                                else:
                                    st.error(f"❌ {msg}")
                                st.session_state.confirm_delete_cug = None
                                st.rerun()
                            if confirm_cols[1].button("Cancel", key=f"cancel_inst_{cug}"):
                                st.session_state.confirm_delete_cug = None
                                st.rerun()
                            confirm_cols[2].warning(f"⚠️ Remove **{name}** ({cug})?")
                        else:
                            if row_cols[2].button("🗑️", key=f"del_inst_{cug}", help=f"Remove {name}"):
                                st.session_state.confirm_delete_cug = cug
                                st.rerun()

        # ── 3. Add Supervisor / Assign Installer Forms ────────────────────────
        st.divider()
        col1, col2 = st.columns(2)

        # Add Supervisor Form
        with col1:
            st.subheader("➕ Add a Supervisor")
            if "sup_form_key" not in st.session_state:
                st.session_state.sup_form_key = 0

            with st.form(f"sup_form_{st.session_state.sup_form_key}", clear_on_submit=True):
                new_sup_username = st.text_input("Supervisor Username")
                new_sup_password = st.text_input("Password", type="password")
                new_sup_shop     = st.text_input("Shop Name they Supervise")
                submit_sup       = st.form_submit_button("Create Supervisor", use_container_width=True)

                if submit_sup:
                    u = new_sup_username.strip()
                    p = new_sup_password.strip()
                    s = new_sup_shop.strip()
                    if not u or not p or not s:
                        st.error("⚠️ All fields are required.")
                    else:
                        success, msg = create_supervisor(u, p, s)
                        if success:
                            st.success(f"✅ Supervisor **{u}** created for shop **{s}**!")
                            st.session_state.sup_form_key += 1
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

        # Assign Installer Form
        with col2:
            st.subheader("👷 Assign an Installer")
            if "inst_form_key" not in st.session_state:
                st.session_state.inst_form_key = 0

            sup_usernames = [s.get("username") for s in supervisors] if supervisors else []

            with st.form(f"inst_form_{st.session_state.inst_form_key}", clear_on_submit=True):
                new_cug           = st.text_input("Installer CUG Number", placeholder="e.g. 978982901")
                new_name          = st.text_input("Installer Full Name")
                selected_sup_form = st.selectbox(
                    "Assign to Supervisor",
                    sup_usernames if sup_usernames else ["— Create a supervisor first —"],
                )
                submit_inst = st.form_submit_button("Add Installer", use_container_width=True)

                if submit_inst:
                    cug  = new_cug.strip()
                    name = new_name.strip()
                    if not cug or not name or not sup_usernames:
                        st.error("⚠️ All fields are required.")
                    else:
                        valid, err = validate_cug(cug)
                        if not valid:
                            st.error(f"❌ Invalid CUG — {err}")
                        else:
                            success, msg = add_installer(cug, name, selected_sup_form)
                            if success:
                                st.success(f"✅ **{name}** (CUG: {cug}) assigned to **{selected_sup_form}**!")
                                st.session_state.inst_form_key += 1
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
