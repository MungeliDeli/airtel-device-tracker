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

def get_all_shops():
    db = get_db()
    if db is not None:
        return list(db.shops.find())
    return []

def get_installers_by_shop(shop_id):
    db = get_db()
    if db is not None:
        return list(db.installers.find({"shop_id": shop_id}))
    return []

def get_all_installers():
    db = get_db()
    if db is not None:
        return list(db.installers.find())
    return []
