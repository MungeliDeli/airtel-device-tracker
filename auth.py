import streamlit as st
from database import get_user
import hmac

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        username = st.session_state["username_input"]
        password = st.session_state["password_input"]
        
        user_doc = get_user(username)
        
        if user_doc:
            # We are using simple string comparison for this example,
            # but in production we should use hashed passwords!
            if password == user_doc.get("password_hash", ""):
                st.session_state["password_correct"] = True
                st.session_state["logged_in_user"] = username
                st.session_state["role"] = user_doc.get("role", "supervisor")
                st.session_state["shop_name"] = user_doc.get("shop_name", "Admin")
                del st.session_state["password_input"]  # clear from memory
                return

        st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Show input for credentials
    st.title("Airtel Shop Tracker - Login")
    
    st.text_input("Username", key="username_input")
    st.text_input("Password", type="password", key="password_input")
    st.button("Login", on_click=password_entered)
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 User not known or password incorrect")
        
    return False

def logout():
    """Logs the user out by clearing session state."""
    keys_to_clear = ["password_correct", "logged_in_user", "role", "shop_name"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
