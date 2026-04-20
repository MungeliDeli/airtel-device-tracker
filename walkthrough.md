# V2 Architecture Walkthrough

I have scaffolded the complete V2 architecture in the `c:\Users\davym\OneDrive\Desktop\Arcades\v2\` folder. Your original `app.py` remains untouched and safe!

## What was built?

We broke down the massive 500-line `app.py` into distinct, focused modules. This makes the code significantly easier to maintain, debug, and expand.

### 1. `app.py` (The Entry Point)
This is the new main file. Its only job is to:
- Render the login screen via `auth.py`.
- Check the user's role (Admin vs. Supervisor).
- Route the user to the correct dashboard based on their role.

### 2. `auth.py`
Handles all authentication logic. It checks the credentials entered against the MongoDB database and securely stores the user's `role` and `shop_id` in the Streamlit Session State so the app remembers who is logged in.

### 3. `database.py`
This is the single source of truth for interacting with MongoDB Atlas. It contains functions to:
- Connect to the database (`@st.cache_resource` for speed).
- Fetch user credentials.
- Fetch shops and the installers assigned to them.

### 4. `kobo_api.py` & `google_sheets_api.py`
We isolated the data fetching logic. 
- `kobo_api.py` handles the API calls to KoboToolbox.
- `google_sheets_api.py` handles reading the CSV export directly from your Google Sheet (no more file uploads!).

### 5. `views/admin_dashboard.py`
The dedicated UI for Admins. It allows admins to:
- View the performance of **all** shops combined.
- Manage the database (e.g., UI forms to add new installers to specific shops).

### 6. `views/supervisor_dashboard.py`
The dedicated UI for Supervisors. 
- It uses the `shop_id` saved during login to **filter** the Kobo and Google Sheets data.
- Supervisors will **only** see the performance metrics and sign-out reconciliation for the installers assigned to their specific shop.

## How to Review

1. Open your code editor and look inside the `v2/` folder.
2. Read through `app.py` first, then trace how it calls `auth.py` and the `views/`.
3. You will notice how much cleaner the dashboards are now that the heavy data-fetching logic is hidden away in the API files.

## Next Steps for Deployment

To make this functional, you will need to:
1. Create a free **MongoDB Atlas** cluster and put the connection URI in your `.streamlit/secrets.toml`.
2. Ensure you have the `streamlit-authenticator` and `pymongo` libraries added to your `requirements.txt` file (or `Core Requirements.txt`).
3. Add a few test users and shops directly into the MongoDB Atlas database to test the login!
