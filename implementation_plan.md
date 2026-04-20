# Modular Streamlit App with MongoDB Atlas & RBAC

This document outlines the architecture, database schema, and steps to transform the existing `app.py` into a modular application using MongoDB Atlas for user management and Role-Based Access Control (RBAC).

## Goal Description

The current Streamlit application is a single `app.py` file with hardcoded installers (`TEAM_MEMBERS`). 
We will transition this into a modular application backed by **MongoDB Atlas**. This will introduce two distinct user roles:
1. **Admins:** Can create supervisors, assign installers to specific shops, and view the performance of *all* shops.
2. **Supervisors:** Can only log in and view the performance metrics and sign-out reconciliation for the installers assigned to their specific shop.

> [!NOTE]
> As requested, this is **just a plan**. No code has been written or modified yet.

## User Review Required

- **MongoDB Account:** You will need to create a free MongoDB Atlas cluster and obtain the connection string (`mongodb+srv://...`) before we can execute the code.
- **Authentication Method:** We plan to use `streamlit-authenticator` to handle secure login forms and password hashing. This requires adding a new dependency (`pip install streamlit-authenticator`).
- **Initial Admin User:** When we first boot the new app, it will need a way to create the very first "Admin" user. We will write a small script to bootstrap this.

## Open Questions

- **Sign-out Data Storage:** Do you want to continue uploading the Excel file for "Sign-out" data, or would you like to build a data-entry form for supervisors in the app so sign-outs are saved directly to MongoDB Atlas? (For now, the plan assumes we keep the file upload logic but modularize it).

## Proposed Changes

We will split the massive 500-line `app.py` into a clean, modular directory structure.

### `database.py`
Handles all connections to MongoDB Atlas and CRUD (Create, Read, Update, Delete) operations.
#### [NEW] `database.py`
- Initialize MongoDB connection using `@st.cache_resource`.
- Functions: `get_user()`, `create_user()`, `get_installers_for_shop()`, `get_all_shops()`, `add_installer()`.

---

### `auth.py`
Manages user sessions, login state, and security.
#### [NEW] `auth.py`
- Uses `streamlit-authenticator` or custom logic to render the login screen.
- Sets `st.session_state["role"]` and `st.session_state["shop_id"]` upon successful login.

---

### `kobo_api.py`
Isolates the external API logic.
#### [NEW] `kobo_api.py`
- Moves `fetch_kobo_data()`, `load_kobo()`, and column resolution out of the main UI file.

---

### Views / Pages
Separates the UI into distinct files based on the logged-in role.

#### [NEW] `views/admin_dashboard.py`
- **User Management Tab:** Forms to create new supervisor accounts.
- **Shop Management Tab:** Forms to add installers (CUG numbers and names) to specific shops.
- **Global Overview Tab:** The existing "Team Performance" view, but showing all shops combined.

#### [NEW] `views/supervisor_dashboard.py`
- Contains the existing "Team Performance" and "Device Management" logic.
- **Crucial Difference:** The data fetched from Kobo is immediately filtered using the `shop_id` from the session state, so the supervisor only sees their own team.

---

### Main Entry Point
#### [MODIFY] `app.py`
- Replaced almost entirely. 
- It will now only check authentication via `auth.py`.
- If logged in as Admin, it routes to `views/admin_dashboard.py`.
- If logged in as Supervisor, it routes to `views/supervisor_dashboard.py`.

---

## MongoDB Atlas Schema Design

We will use three main collections in your MongoDB database:

1. **`users`**
   - `_id`: Auto-generated
   - `username`: String (e.g., "admin_davy", "shop_arcade_super")
   - `password_hash`: String (Securely hashed)
   - `role`: String ("admin" or "supervisor")
   - `shop_id`: ObjectId (Null if admin)

2. **`shops`**
   - `_id`: Auto-generated ObjectId
   - `name`: String (e.g., "Arcades Mall Shop")

3. **`installers`**
   - `_id`: Auto-generated
   - `cug_number`: String (e.g., "978982901")
   - `name`: String (e.g., "Li David Mumba")
   - `shop_id`: ObjectId (Links the installer to a specific shop)

## Verification Plan

### Database Connection
- Write a quick test script to verify Streamlit can connect to the provided MongoDB Atlas URI.

### Role-Based Access Verification
- Create 1 Admin and 2 different Supervisors in the database.
- Log in as Supervisor A and verify only Shop A's CUG numbers appear in the data tables.
- Log in as Supervisor B and verify only Shop B's CUG numbers appear.
- Log in as Admin and verify the ability to see both, and the UI to add a new installer to Shop A works and persists in the database.
