# Airtel Shop Tracker

A simple Streamlit app for supervisors to reconcile device sign-outs against KoboToolbox installations.

## Setup (one time)

### 1. GitHub
- Create a free account at github.com
- Create a new repository (e.g. `airtel-tracker`)
- Upload `app.py` and `requirements.txt` into it

### 2. Streamlit Community Cloud
- Go to share.streamlit.io and sign in with your GitHub account
- Click "New app"
- Select your repository and set the main file to `app.py`
- Click "Deploy" — your app will be live in ~2 minutes at a public URL

### 3. Google Form columns
Your Google Form sign-out CSV must have these exact column names
(or edit the `FORM_COLS` section at the top of app.py to match yours):

| Field          | Expected column name    |
|----------------|-------------------------|
| Installer CUG  | `Installer CUG`         |
| IMEI           | `IMEI Number`           |
| Timestamp      | `Timestamp`             |

Google Forms auto-adds a `Timestamp` column — no action needed for that one.

## Daily use

1. Open Google Sheet → File → Download → CSV  
2. Open KoboToolbox → Data → Downloads → CSV  
3. Go to the app URL  
4. Upload both files  
5. Set date filter → report is ready  
6. Use the download button to export for the boss  
