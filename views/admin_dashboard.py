import streamlit as st
from database import (
    get_supervisors, create_supervisor,
    add_installer, get_installers_by_supervisor, remove_installer
)
import pandas as pd


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
        st.info("Here we will show the combined metrics for ALL installers across ALL supervisors.")
        st.write("Placeholder: Kobo Data aggregation will appear here.")

    elif app_mode == "Manage Supervisors & Installers":
        st.header("Manage Supervisors & Installers")

        supervisors = get_supervisors()

        # ── 1. Summary Table ──────────────────────────────────────────────────
        st.subheader("Current Supervisors")
        if not supervisors:
            st.warning("No supervisors found in database yet.")
        else:
            table_data = []
            for sup in supervisors:
                username  = sup.get("username")
                shop_name = sup.get("shop_name", "Unknown")
                count     = len(get_installers_by_supervisor(username))
                table_data.append({
                    "Supervisor Username":  username,
                    "Shop Name":           shop_name,
                    "Number of Installers": count,
                })
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

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

                    # Initialise confirm-delete state
                    if "confirm_delete_cug" not in st.session_state:
                        st.session_state.confirm_delete_cug = None

                    # Render each installer as a row with a delete button
                    header_cols = st.columns([3, 3, 1])
                    header_cols[0].markdown("**Installer Name**")
                    header_cols[1].markdown("**CUG Number**")
                    header_cols[2].markdown("**Remove**")

                    for inst in installers:
                        cug  = inst.get("cug_number")
                        name = inst.get("name")

                        row_cols = st.columns([3, 3, 1])
                        row_cols[0].write(name)
                        row_cols[1].write(cug)

                        # First click → ask for confirmation
                        if st.session_state.confirm_delete_cug == cug:
                            # Show inline confirmation
                            confirm_cols = st.columns([3, 1, 1])
                            confirm_cols[0].warning(
                                f"⚠️ Are you sure you want to remove **{name}** ({cug})?"
                            )
                            if confirm_cols[1].button("Yes, remove", key=f"yes_{cug}", type="primary"):
                                success, msg = remove_installer(cug)
                                if success:
                                    st.success(f"✅ **{name}** has been removed.")
                                else:
                                    st.error(f"❌ {msg}")
                                st.session_state.confirm_delete_cug = None
                                st.rerun()
                            if confirm_cols[2].button("Cancel", key=f"cancel_{cug}"):
                                st.session_state.confirm_delete_cug = None
                                st.rerun()
                        else:
                            if row_cols[2].button("🗑️", key=f"del_{cug}", help=f"Remove {name}"):
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
                new_cug      = st.text_input("Installer CUG Number", placeholder="e.g. 978982901")
                new_name     = st.text_input("Installer Full Name")
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
