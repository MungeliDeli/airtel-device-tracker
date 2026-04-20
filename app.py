import streamlit as st
import auth

# Set page config FIRST
st.set_page_config(page_title="Airtel Shop Tracker V2", layout="wide")

# CSS Styling
st.markdown("""
<style>
.metric-card {
    background: #f8f9fa; border-radius: 10px;
    padding: 16px 20px; border-left: 4px solid #e0e0e0;
}
.metric-card.green  { border-left-color: #2ecc71; }
.metric-card.blue   { border-left-color: #3498db; }
.metric-card.orange { border-left-color: #e67e22; }
.metric-card.red    { border-left-color: #e74c3c; }
.metric-val { font-size: 2rem; font-weight: 700; margin: 4px 0; }
.metric-lbl { font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 0.05em; }
.section-title {
    font-size: 1.1rem; font-weight: 600;
    border-bottom: 2px solid #e74c3c;
    padding-bottom: 6px; margin: 24px 0 12px;
}
</style>
""", unsafe_allow_html=True)

# Main Authentication Flow
if not auth.check_password():
    st.stop()

# If we get here, the user is logged in
role = st.session_state.get("role")

st.sidebar.title("Airtel Tracker")

# Navigation in the middle
st.sidebar.header("Navigation")
if role == "admin":
    app_mode = st.sidebar.radio("Go to:", ["Global Performance", "Manage Supervisors & Installers"])
elif role == "supervisor":
    app_mode = st.sidebar.radio("Go to:", ["Team Performance", "Device Reconciliation"])
else:
    app_mode = None

st.sidebar.divider()

# Bottom of sidebar for user info
st.sidebar.write(f"Logged in as: **{st.session_state['logged_in_user']}**")
st.sidebar.write(f"Role: **{st.session_state['role'].capitalize()}**")

if st.sidebar.button("Logout"):
    auth.logout()
    st.rerun()

# Route to the appropriate view based on role
if role == "admin":
    from views import admin_dashboard
    admin_dashboard.show(app_mode)
elif role == "supervisor":
    from views import supervisor_dashboard
    supervisor_dashboard.show(app_mode)
else:
    st.error("Unknown role encountered.")
