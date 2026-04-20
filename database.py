import streamlit as st
import pymongo

@st.cache_resource
def init_connection():
    """Initializes and returns the MongoDB connection."""
    try:
        # We will need the URI in .streamlit/secrets.toml under [mongo] uri="..."
        client = pymongo.MongoClient(st.secrets["mongo"]["uri"])
        return client
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def get_db():
    client = init_connection()
    if client:
        return client.airtel_tracker_db
    return None

def get_user(username):
    db = get_db()
    if db is not None:
        return db.users.find_one({"username": username})
    return None

def get_supervisors():
    db = get_db()
    if db is not None:
        return list(db.users.find({"role": "supervisor"}))
    return []

def create_supervisor(username, password_hash, shop_name):
    db = get_db()
    if db is not None:
        if db.users.find_one({"username": username}):
            return False, "Username already exists."
        db.users.insert_one({
            "username": username,
            "password_hash": password_hash,
            "role": "supervisor",
            "shop_name": shop_name
        })
        return True, "Supervisor created successfully."
    return False, "Database connection error."

def get_installers_by_supervisor(supervisor_username):
    db = get_db()
    if db is not None:
        return list(db.installers.find({"supervisor_username": supervisor_username}))
    return []

def get_all_installers():
    db = get_db()
    if db is not None:
        return list(db.installers.find())
    return []

def add_installer(cug_number, name, supervisor_username):
    db = get_db()
    if db is not None:
        if db.installers.find_one({"cug_number": cug_number}):
            return False, "CUG Number already exists."
        db.installers.insert_one({
            "cug_number": cug_number,
            "name": name,
            "supervisor_username": supervisor_username
        })
        return True, "Installer assigned successfully."
    return False, "Database connection error."

def remove_installer(cug_number):
    db = get_db()
    if db is not None:
        result = db.installers.delete_one({"cug_number": cug_number})
        if result.deleted_count > 0:
            return True, "Installer removed successfully."
        return False, "Installer not found."
    return False, "Database connection error."
