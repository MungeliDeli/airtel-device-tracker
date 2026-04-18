import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="Airtel Shop Tracker", page_icon="📡", layout="wide")

# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.metric-card {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 16px 20px;
    border-left: 4px solid #e0e0e0;
}
.metric-card.green  { border-left-color: #2ecc71; }
.metric-card.blue   { border-left-color: #3498db; }
.metric-card.orange { border-left-color: #e67e22; }
.metric-card.red    { border-left-color: #e74c3c; }
.metric-val { font-size: 2rem; font-weight: 700; margin: 4px 0; }
.metric-lbl { font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 0.05em; }
.flag-badge {
    background: #fff3cd; color: #856404;
    border-radius: 6px; padding: 2px 8px;
    font-size: 0.78rem; font-weight: 600;
}
.section-title {
    font-size: 1.1rem; font-weight: 600;
    border-bottom: 2px solid #e74c3c;
    padding-bottom: 6px; margin: 24px 0 12px;
}
</style>
""", unsafe_allow_html=True)

# ── Kobo column names (exact as exported) ────────────────────────────────────
KOBO_COLS = {
    "cug":      "Installer Number (CUG)",
    "phone":    "Correct Customer Phone Number",
    "area":     "Area of Installation ",   # trailing space is in the CSV
    "imei":     "IIMEI Number",
    "odu":      "ODU Number",
    "date":     "Submission Date",
}

# ── Google Form / Sheet column names ─────────────────────────────────────────
# Change these to match whatever your Google Form export looks like
FORM_COLS = {
    "cug":  "Installer CUG",     # installer CUG number
    "imei": "IMEI Number",       # IMEI scanned by barcode
    "date": "Timestamp",         # auto-timestamp from Google Forms
}

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.title("📡 Airtel Shop Tracker")
st.caption("Upload the sign-out CSV and the KoboToolbox CSV to generate your report.")

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — uploads + filters
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Upload Files")

    signout_file = st.file_uploader(
        "1. Sign-out CSV (Google Sheet export)",
        type="csv",
        help="Export from the Google Sheet linked to your sign-out form."
    )
    kobo_file = st.file_uploader(
        "2. KoboToolbox CSV (installs)",
        type="csv",
        help="Download from KoboToolbox → Data → Downloads → CSV."
    )

    st.divider()
    st.header("🗓 Date Filter")
    filter_mode = st.radio(
        "Show data for:",
        ["Today", "This week", "Custom range"],
        index=1
    )
    today = datetime.today().date()
    if filter_mode == "Today":
        date_from, date_to = today, today
    elif filter_mode == "This week":
        date_from = today - timedelta(days=today.weekday())
        date_to = today
    else:
        date_from = st.date_input("From", today - timedelta(days=7))
        date_to   = st.date_input("To",   today)

    st.divider()
    st.caption("Built for Airtel Shop Supervisor")

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def load_kobo(file):
    df = pd.read_csv(file, dtype=str)
    df.columns = df.columns.str.strip()
    # fix the trailing-space column name
    rename = {v.strip(): v for v in KOBO_COLS.values()}
    df = df.rename(columns=rename)
    needed = list(KOBO_COLS.values())
    missing = [c for c in needed if c not in df.columns]
    if missing:
        st.error(f"Kobo CSV is missing columns: {missing}\n\nFound: {list(df.columns)}")
        return None
    df = df[needed].copy()
    df.columns = ["cug", "phone", "area", "imei", "odu", "date"]
    df["date"]  = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["imei"]  = df["imei"].str.strip()
    df["cug"]   = df["cug"].str.strip()
    return df

def load_signout(file):
    df = pd.read_csv(file, dtype=str)
    df.columns = df.columns.str.strip()
    # Try to find columns flexibly
    col_map = {}
    for key, name in FORM_COLS.items():
        if name in df.columns:
            col_map[name] = key
        else:
            # try case-insensitive match
            match = [c for c in df.columns if c.lower() == name.lower()]
            if match:
                col_map[match[0]] = key
    if len(col_map) < 3:
        st.error(
            f"Sign-out CSV columns not recognised.\n\n"
            f"Expected columns named: **{list(FORM_COLS.values())}**\n\n"
            f"Found: {list(df.columns)}\n\n"
            f"👉 Update the `FORM_COLS` section at the top of app.py to match your Google Form export."
        )
        return None
    df = df.rename(columns=col_map)[["cug","imei","date"]].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["imei"] = df["imei"].str.strip()
    df["cug"]  = df["cug"].str.strip()
    return df

def filter_by_date(df, col="date"):
    return df[(df[col] >= date_from) & (df[col] <= date_to)]

def days_ago(d):
    if pd.isna(d):
        return "?"
    delta = (today - d).days
    return "Today" if delta == 0 else f"{delta}d ago"

# ─────────────────────────────────────────────────────────────────────────────
# DEMO MODE — only Kobo uploaded
# ─────────────────────────────────────────────────────────────────────────────
if kobo_file and not signout_file:
    st.info("ℹ️ Only the Kobo file is loaded. Showing **installations only** — upload the sign-out CSV to enable reconciliation.", icon="ℹ️")

    kobo = load_kobo(kobo_file)
    if kobo is None:
        st.stop()

    kobo_f = filter_by_date(kobo)

    st.markdown(f"### Installations — {date_from} to {date_to}")

    installers = sorted(kobo_f["cug"].dropna().unique())
    selected = st.selectbox("Filter by installer CUG (optional)", ["All"] + list(installers))
    view = kobo_f if selected == "All" else kobo_f[kobo_f["cug"] == selected]

    # rename for display
    display = view.rename(columns={
        "cug": "CUG", "phone": "Customer Phone", "area": "Area",
        "imei": "IMEI", "odu": "ODU Number", "date": "Date"
    })
    st.dataframe(display[["CUG","Customer Phone","Area","IMEI","ODU Number","Date"]],
                 use_container_width=True, hide_index=True)

    # Team summary
    st.markdown('<div class="section-title">Team Performance</div>', unsafe_allow_html=True)
    summary = (kobo_f.groupby("cug")
               .agg(Installed=("imei","count"))
               .reset_index()
               .rename(columns={"cug":"Installer CUG"}))
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# FULL MODE — both files
# ─────────────────────────────────────────────────────────────────────────────
if kobo_file and signout_file:
    kobo    = load_kobo(kobo_file)
    signout = load_signout(signout_file)
    if kobo is None or signout is None:
        st.stop()

    kobo_f    = filter_by_date(kobo)
    signout_f = filter_by_date(signout)

    # Reconcile: left-join signed-out → installed
    merged = signout_f.merge(
        kobo_f[["imei","phone","area","odu","date"]].rename(columns={"date":"install_date"}),
        on="imei", how="left"
    )
    merged["status"] = merged["install_date"].apply(
        lambda x: "✅ Installed" if pd.notna(x) else "⚠️ Not installed"
    )
    merged["days_since_signout"] = merged["date"].apply(days_ago)

    # ── Team KPIs ────────────────────────────────────────────────────────────
    total_signed    = len(signout_f)
    total_installed = merged["install_date"].notna().sum()
    total_pending   = total_signed - total_installed
    pct = int(total_installed / total_signed * 100) if total_signed else 0

    st.markdown(f"### 📊 Team Summary — {date_from} to {date_to}")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card blue"><div class="metric-lbl">Total Signed Out</div><div class="metric-val">{total_signed}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card green"><div class="metric-lbl">Installed</div><div class="metric-val">{total_installed}</div></div>', unsafe_allow_html=True)
    with c3:
        col = "orange" if total_pending > 0 else "green"
        st.markdown(f'<div class="metric-card {col}"><div class="metric-lbl">Pending</div><div class="metric-val">{total_pending}</div></div>', unsafe_allow_html=True)
    with c4:
        col = "green" if pct >= 80 else ("orange" if pct >= 50 else "red")
        st.markdown(f'<div class="metric-card {col}"><div class="metric-lbl">Completion Rate</div><div class="metric-val">{pct}%</div></div>', unsafe_allow_html=True)

    st.markdown("")

    # ── Per-installer performance ─────────────────────────────────────────────
    st.markdown('<div class="section-title">👷 Per-Installer Performance</div>', unsafe_allow_html=True)

    perf = (merged.groupby("cug")
            .agg(
                Signed=("imei","count"),
                Installed=("install_date", lambda x: x.notna().sum())
            )
            .reset_index())
    perf["Pending"]         = perf["Signed"] - perf["Installed"]
    perf["Completion %"]    = (perf["Installed"] / perf["Signed"] * 100).round(0).astype(int)
    perf = perf.rename(columns={"cug": "Installer CUG"}).sort_values("Completion %", ascending=False)

    def highlight(row):
        pct_val = row["Completion %"]
        color = "#d4edda" if pct_val >= 80 else ("#fff3cd" if pct_val >= 50 else "#f8d7da")
        return [f"background-color: {color}"] * len(row)

    st.dataframe(
        perf.style.apply(highlight, axis=1),
        use_container_width=True, hide_index=True
    )

    # ── Per-installer drill-down ──────────────────────────────────────────────
    st.markdown('<div class="section-title">🔍 Installer Drill-Down</div>', unsafe_allow_html=True)

    installers = ["All"] + sorted(merged["cug"].dropna().unique().tolist())
    selected_cug = st.selectbox("Select installer", installers)

    view = merged if selected_cug == "All" else merged[merged["cug"] == selected_cug]

    display_cols = {
        "cug":             "Installer CUG",
        "imei":            "IMEI",
        "odu":             "ODU Number",
        "phone":           "Customer Phone",
        "area":            "Area",
        "date":            "Sign-out Date",
        "install_date":    "Install Date",
        "status":          "Status",
        "days_since_signout": "Signed"
    }
    disp = view.rename(columns=display_cols)[list(display_cols.values())]
    st.dataframe(disp, use_container_width=True, hide_index=True)

    # ── Flagged devices ───────────────────────────────────────────────────────
    flagged = merged[merged["install_date"].isna()].copy()
    if not flagged.empty:
        st.markdown(f'<div class="section-title">🚨 Flagged — Signed But Not Installed ({len(flagged)})</div>', unsafe_allow_html=True)
        flag_disp = flagged[["cug","imei","date","days_since_signout"]].rename(columns={
            "cug":"Installer CUG", "imei":"IMEI",
            "date":"Sign-out Date", "days_since_signout":"How long ago"
        })
        st.dataframe(flag_disp, use_container_width=True, hide_index=True)
    else:
        st.success("✅ All signed-out devices have been installed.")

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📥 Export Report</div>', unsafe_allow_html=True)

    export_df = merged.rename(columns={
        "cug":"Installer CUG", "imei":"IMEI", "odu":"ODU Number",
        "phone":"Customer Phone", "area":"Area",
        "date":"Sign-out Date", "install_date":"Install Date", "status":"Status"
    })
    csv_bytes = export_df.to_csv(index=False).encode()
    st.download_button(
        label="⬇️ Download full reconciliation CSV",
        data=csv_bytes,
        file_name=f"airtel_report_{date_from}_to_{date_to}.csv",
        mime="text/csv"
    )

# ─────────────────────────────────────────────────────────────────────────────
# LANDING — nothing uploaded yet
# ─────────────────────────────────────────────────────────────────────────────
if not kobo_file and not signout_file:
    st.markdown("""
    ### How to use this app

    **Step 1** — Export the Google Sheet linked to your sign-out form as a CSV and upload it on the left.

    **Step 2** — Log into KoboToolbox → your project → Data → Downloads → CSV. Upload that file too.

    **Step 3** — Set the date filter and your report is ready instantly.

    ---
    > You can also upload **just the Kobo CSV** to view installations without reconciliation.
    """)
