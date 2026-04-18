import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="Airtel Shop Tracker", page_icon="📡", layout="wide")

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

# ── Column names ──────────────────────────────────────────────────────────────
KOBO_COLS = {
    "cug":   "Installer Number (CUG)",
    "phone": "Correct Customer Phone Number",
    "area":  "Area of Installation",
    "imei":  "IIMEI Number",
    "odu":   "ODU Number",
    "date":  "Submission Date",
}
FORM_COLS = {
    "cug":  "Installer CUG",
    "imei": "IMEI Number",
    "date": "Timestamp",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def read_file(file):
    name = file.name.lower()
    try:
        if name.endswith(".xlsx"):
            df = pd.read_excel(file, dtype=str, engine="openpyxl")
        elif name.endswith(".xls"):
            df = pd.read_excel(file, dtype=str)
        else:
            raw = file.read()
            for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            df = pd.read_csv(io.StringIO(text), dtype=str,
                             on_bad_lines="skip", engine="python")
    except Exception as e:
        st.error(f"❌ Failed to read `{file.name}`: {e}")
        return None
    df.columns = df.columns.str.strip()
    return df


def resolve_columns(df, needed, label="file"):
    col_lookup = {c.strip().lower(): c for c in df.columns}
    rename_map = {}
    missing = []
    for key, canonical in needed.items():
        if canonical in df.columns:
            rename_map[canonical] = key
        else:
            fuzzy = canonical.strip().lower()
            if fuzzy in col_lookup:
                rename_map[col_lookup[fuzzy]] = key
            else:
                missing.append(canonical)
    if missing:
        st.error(f"❌ **{label}** — could not find columns: `{missing}`")
        st.info(f"Columns found in file: `{list(df.columns)}`")
        return None
    return df.rename(columns=rename_map)[list(needed.keys())].copy()


def load_kobo(file):
    df = read_file(file)
    if df is None:
        return None
    df = resolve_columns(df, KOBO_COLS, label="Kobo file")
    if df is None:
        return None
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["imei"] = df["imei"].astype(str).str.strip()
    df["cug"]  = df["cug"].astype(str).str.strip()
    return df


def load_signout(file):
    df = read_file(file)
    if df is None:
        return None
    df = resolve_columns(df, FORM_COLS, label="Sign-out file")
    if df is None:
        return None
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["imei"] = df["imei"].astype(str).str.strip()
    df["cug"]  = df["cug"].astype(str).str.strip()
    return df


def detect_file_type(df):
    cols = {c.strip().lower() for c in df.columns}
    kobo_keys = {v.strip().lower() for v in KOBO_COLS.values()}
    form_keys = {v.strip().lower() for v in FORM_COLS.values()}
    if kobo_keys.issubset(cols):
        return "kobo"
    if form_keys.issubset(cols):
        return "signout"
    if len(kobo_keys & cols) >= 4:
        return "kobo"
    if len(form_keys & cols) >= 2:
        return "signout"
    return None


def filter_by_date(df, col="date"):
    return df[(df[col] >= date_from) & (df[col] <= date_to)]


def days_ago(d):
    if pd.isna(d):
        return "?"
    delta = (today - d).days
    return "Today" if delta == 0 else f"{delta}d ago"

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.title("📡 Airtel Shop Tracker")
st.caption("Upload the Kobo xlsx and the sign-out file to generate your report.")

with st.sidebar:
    st.header("📂 Upload Files")
    kobo_file = st.file_uploader(
        "1. KoboToolbox export (.xlsx)",
        type=["xlsx", "xls", "csv"],
    )
    signout_file = st.file_uploader(
        "2. Sign-out file (Google Sheet export)",
        type=["xlsx", "xls", "csv"],
    )
    st.divider()
    st.header("🗓 Date Filter")
    filter_mode = st.radio("Show data for:", ["Today", "This week", "Custom range"], index=1)
    today = datetime.today().date()
    if filter_mode == "Today":
        date_from = date_to = today
    elif filter_mode == "This week":
        date_from = today - timedelta(days=today.weekday())
        date_to   = today
    else:
        date_from = st.date_input("From", today - timedelta(days=7))
        date_to   = st.date_input("To",   today)
    st.divider()

    # ── DEBUG TOGGLE ──────────────────────────────────────────────────────────
    debug = st.checkbox("🛠 Show debug info", value=False)
    st.caption("Built for Airtel Shop Supervisor")

# ── LANDING ───────────────────────────────────────────────────────────────────
if not kobo_file and not signout_file:
    st.markdown("""
    ### How to use this app
    **Step 1 — Kobo file:** KoboToolbox → Data → Downloads → **XLS** → open in Excel → Save As → **.xlsx** → upload here.

    **Step 2 — Sign-out file:** Google Sheet → File → Download → **.xlsx** → upload here.

    **Step 3:** Set the date filter. Report is ready instantly.

    ---
    > You can upload **just the Kobo file** to browse installations without reconciliation.
    """)
    st.stop()

# ── KOBO ONLY ─────────────────────────────────────────────────────────────────
if kobo_file and not signout_file:
    st.info("Showing **installations only**. Upload the sign-out file too to enable reconciliation.", icon="ℹ️")

    kobo = load_kobo(kobo_file)

    if debug:
        if kobo is not None:
            st.success(f"✅ Kobo loaded: {len(kobo)} rows")
            st.write("**Column names found:**", list(kobo.columns))
            st.write("**First 3 rows:**")
            st.dataframe(kobo.head(3))
        else:
            st.warning("Kobo returned None — see error above.")

    if kobo is None:
        st.stop()

    kobo_f = filter_by_date(kobo)

    if debug:
        st.info(f"After date filter ({date_from} → {date_to}): {len(kobo_f)} rows")

    if kobo_f.empty:
        st.warning(f"No installations found between {date_from} and {date_to}. Try changing the date filter.")
        st.stop()

    st.markdown(f"### Installations — {date_from} to {date_to}")
    installers = ["All"] + sorted(kobo_f["cug"].dropna().unique().tolist())
    selected   = st.selectbox("Filter by installer CUG", installers)
    view = kobo_f if selected == "All" else kobo_f[kobo_f["cug"] == selected]

    disp = view.rename(columns={
        "cug":"Installer CUG","phone":"Customer Phone",
        "area":"Area","imei":"IMEI","odu":"ODU Number","date":"Date"
    })
    st.dataframe(disp[["Installer CUG","Customer Phone","Area","IMEI","ODU Number","Date"]],
                 use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">Team Performance</div>', unsafe_allow_html=True)
    summary = (kobo_f.groupby("cug")
               .agg(Installed=("imei","count"))
               .reset_index()
               .rename(columns={"cug":"Installer CUG"})
               .sort_values("Installed", ascending=False))
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.stop()

# ── SIGN-OUT ONLY ───────────────────────────────────────────────────────────────
if signout_file and not kobo_file:
    signout = None
    df = read_file(signout_file)
    detected = detect_file_type(df) if df is not None else None

    if detected == "kobo":
        st.warning("This upload looks like a Kobo export. Showing Kobo installations instead.")
        kobo = load_kobo(signout_file)

        if debug:
            if kobo is not None:
                st.success(f"✅ Kobo loaded: {len(kobo)} rows")
                st.write("**Column names found:**", list(kobo.columns))
                st.write("**First 3 rows:**")
                st.dataframe(kobo.head(3))
            else:
                st.warning("Kobo returned None — see error above.")

        if kobo is None:
            st.stop()

        kobo_f = filter_by_date(kobo)

        if debug:
            st.info(f"After date filter ({date_from} → {date_to}): {len(kobo_f)} rows")

        if kobo_f.empty:
            st.warning(f"No installations found between {date_from} and {date_to}. Try changing the date filter.")
            st.stop()

        st.markdown(f"### Installations — {date_from} to {date_to}")
        installers = ["All"] + sorted(kobo_f["cug"].dropna().unique().tolist())
        selected   = st.selectbox("Filter by installer CUG", installers)
        view = kobo_f if selected == "All" else kobo_f[kobo_f["cug"] == selected]

        disp = view.rename(columns={
            "cug":"Installer CUG","phone":"Customer Phone",
            "area":"Area","imei":"IMEI","odu":"ODU Number","date":"Date"
        })
        st.dataframe(disp[["Installer CUG","Customer Phone","Area","IMEI","ODU Number","Date"]],
                     use_container_width=True, hide_index=True)

        st.markdown('<div class="section-title">Team Performance</div>', unsafe_allow_html=True)
        summary = (kobo_f.groupby("cug")
                   .agg(Installed=("imei","count"))
                   .reset_index()
                   .rename(columns={"cug":"Installer CUG"})
                   .sort_values("Installed", ascending=False))
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.stop()

    st.info("Showing **sign-out data only**. Upload the Kobo file to reconcile installations.", icon="ℹ️")
    signout = load_signout(signout_file)

    if debug:
        if signout is not None:
            st.success(f"✅ Sign-out loaded: {len(signout)} rows")
            st.write("**Column names found:**", list(signout.columns))
            st.write("**First 3 rows:**")
            st.dataframe(signout.head(3))
        else:
            st.warning("Sign-out returned None — see error above.")

    if signout is None:
        st.stop()

    signout_f = filter_by_date(signout)

    if debug:
        st.info(f"Sign-out after date filter ({date_from} → {date_to}): {len(signout_f)} rows")

    if signout_f.empty:
        st.warning(f"No sign-outs found between {date_from} and {date_to}. Try changing the date filter.")
        st.stop()

    st.markdown(f"### Sign-outs — {date_from} to {date_to}")
    installers = ["All"] + sorted(signout_f["cug"].dropna().unique().tolist())
    selected   = st.selectbox("Filter by installer CUG", installers)
    view = signout_f if selected == "All" else signout_f[signout_f["cug"] == selected]

    disp = view.rename(columns={
        "cug":"Installer CUG","imei":"IMEI","date":"Sign-out Date"
    })
    st.dataframe(disp[["Installer CUG","IMEI","Sign-out Date"]],
                 use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">Team Performance</div>', unsafe_allow_html=True)
    summary = (signout_f.groupby("cug")
               .agg(Signed_Out=("imei","count"))
               .reset_index()
               .rename(columns={"cug":"Installer CUG"})
               .sort_values("Signed_Out", ascending=False))
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.stop()

# ── FULL MODE ─────────────────────────────────────────────────────────────────
if kobo_file and signout_file:
    kobo    = load_kobo(kobo_file)
    signout = load_signout(signout_file)

    if debug:
        if kobo is not None:
            st.success(f"✅ Kobo loaded: {len(kobo)} rows")
            st.write("**Kobo columns:**", list(kobo.columns))
            st.dataframe(kobo.head(3))
        if signout is not None:
            st.success(f"✅ Sign-out loaded: {len(signout)} rows")
            st.write("**Sign-out columns:**", list(signout.columns))
            st.dataframe(signout.head(3))

    if kobo is None or signout is None:
        st.stop()

    kobo_f    = filter_by_date(kobo)
    signout_f = filter_by_date(signout)

    if debug:
        st.info(f"Kobo after filter: {len(kobo_f)} rows | Sign-out after filter: {len(signout_f)} rows")

    if kobo_f.empty and signout_f.empty:
        st.warning(f"No data found between {date_from} and {date_to}. Try changing the date filter.")
        st.stop()

    merged = signout_f.merge(
        kobo_f[["imei","phone","area","odu","date"]].rename(columns={"date":"install_date"}),
        on="imei", how="left"
    )
    merged["status"]             = merged["install_date"].apply(
        lambda x: "✅ Installed" if pd.notna(x) else "⚠️ Not installed")
    merged["days_since_signout"] = merged["date"].apply(days_ago)

    total_signed    = len(signout_f)
    total_installed = int(merged["install_date"].notna().sum())
    total_pending   = total_signed - total_installed
    pct             = int(total_installed / total_signed * 100) if total_signed else 0

    st.markdown(f"### 📊 Team Summary — {date_from} to {date_to}")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card blue"><div class="metric-lbl">Signed Out</div><div class="metric-val">{total_signed}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card green"><div class="metric-lbl">Installed</div><div class="metric-val">{total_installed}</div></div>', unsafe_allow_html=True)
    with c3:
        c = "orange" if total_pending > 0 else "green"
        st.markdown(f'<div class="metric-card {c}"><div class="metric-lbl">Pending</div><div class="metric-val">{total_pending}</div></div>', unsafe_allow_html=True)
    with c4:
        c = "green" if pct >= 80 else ("orange" if pct >= 50 else "red")
        st.markdown(f'<div class="metric-card {c}"><div class="metric-lbl">Completion</div><div class="metric-val">{pct}%</div></div>', unsafe_allow_html=True)

    st.markdown("")

    st.markdown('<div class="section-title">👷 Per-Installer Performance</div>', unsafe_allow_html=True)
    perf = (merged.groupby("cug")
            .agg(Signed=("imei","count"),
                 Installed=("install_date", lambda x: x.notna().sum()))
            .reset_index())
    perf["Pending"]      = perf["Signed"] - perf["Installed"]
    perf["Completion %"] = (perf["Installed"] / perf["Signed"] * 100).round(0).astype(int)
    perf = perf.rename(columns={"cug":"Installer CUG"}).sort_values("Completion %", ascending=False)

    def highlight(row):
        v = row["Completion %"]
        color = "#d4edda" if v >= 80 else ("#fff3cd" if v >= 50 else "#f8d7da")
        return [f"background-color: {color}"] * len(row)

    st.dataframe(perf.style.apply(highlight, axis=1), use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">🔍 Installer Drill-Down</div>', unsafe_allow_html=True)
    options      = ["All"] + sorted(merged["cug"].dropna().unique().tolist())
    selected_cug = st.selectbox("Select installer", options)
    view = merged if selected_cug == "All" else merged[merged["cug"] == selected_cug]

    disp = view.rename(columns={
        "cug":"Installer CUG","imei":"IMEI","odu":"ODU Number",
        "phone":"Customer Phone","area":"Area","date":"Sign-out Date",
        "install_date":"Install Date","status":"Status","days_since_signout":"Signed"
    })
    st.dataframe(
        disp[["Installer CUG","IMEI","ODU Number","Customer Phone","Area",
              "Sign-out Date","Install Date","Status","Signed"]],
        use_container_width=True, hide_index=True)

    flagged = merged[merged["install_date"].isna()].copy()
    if not flagged.empty:
        st.markdown(f'<div class="section-title">🚨 Flagged — Signed But Not Installed ({len(flagged)})</div>', unsafe_allow_html=True)
        flag_disp = flagged[["cug","imei","date","days_since_signout"]].rename(columns={
            "cug":"Installer CUG","imei":"IMEI",
            "date":"Sign-out Date","days_since_signout":"How long ago"})
        st.dataframe(flag_disp, use_container_width=True, hide_index=True)
    else:
        st.success("✅ All signed-out devices have been installed.")

    st.markdown('<div class="section-title">📥 Export Report</div>', unsafe_allow_html=True)
    export_df = merged.rename(columns={
        "cug":"Installer CUG","imei":"IMEI","odu":"ODU Number",
        "phone":"Customer Phone","area":"Area",
        "date":"Sign-out Date","install_date":"Install Date","status":"Status"})
    st.download_button(
        label="⬇️ Download full reconciliation CSV",
        data=export_df.to_csv(index=False).encode(),
        file_name=f"airtel_report_{date_from}_to_{date_to}.csv",
        mime="text/csv")
