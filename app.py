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

# ── Configuration & Data ──────────────────────────────────────────────────────
TEAM_MEMBERS = {
    "978982901": "Li David Mumba",
    "978982172": "Weston Daka",
    "978982561": "Karren Kamulosu",
    "978982985": "Reagan Makayi",
    "978982922": "Jonathan Chatila",
    "978982955": "Shadreck Soko",
    "978982611": "Constance Chilamo",
    "978982623": "Davy Mwansa",
    "978982926": "George Banda",
    "978982933": "Erick Halale",
    "978982856": "Guardian Mwenya",
    "978982909": "Harrison Mbewe",
    "978982798": "Fredrick Kwaleyela"
}

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

def filter_by_date(df, date_from, date_to, col="date"):
    return df[(df[col] >= date_from) & (df[col] <= date_to)]

def days_ago(d, today):
    if pd.isna(d):
        return "?"
    delta = (today - d).days
    return "Today" if delta == 0 else f"{delta}d ago"

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.title("📡 Airtel Shop Tracker")
st.caption("Track device sign-outs and team installation performance.")

with st.sidebar:
    st.header("🧭 Navigation")
    app_mode = st.radio("Go to:", ["Team Performance", "Device Management"])
    
    st.divider()
    st.header("📂 Upload Files")
    kobo_file = st.file_uploader(
        "1. KoboToolbox export (.xlsx)",
        type=["xlsx", "xls", "csv"],
    )
    
    signout_file = None
    if app_mode == "Device Management":
        signout_file = st.file_uploader(
            "2. Sign-out file (Google Sheet export)",
            type=["xlsx", "xls", "csv"],
        )

    st.divider()
    debug = st.checkbox("🛠 Show debug info", value=False)
    st.caption("Built for Airtel Shop Supervisor")

today_dt = datetime.today().date()

# ── TEAM PERFORMANCE ──────────────────────────────────────────────────────────
if app_mode == "Team Performance":
    if not kobo_file:
        st.info("👋 Welcome to Team Performance. Please upload the **KoboToolbox export (.xlsx)** in the sidebar to view the dashboard.")
        st.stop()
        
    kobo = load_kobo(kobo_file)
    if kobo is None:
        st.stop()
        
    # Filter for our specific team members
    kobo_team = kobo[kobo["cug"].isin(TEAM_MEMBERS.keys())].copy()
    kobo_team["Installer Name"] = kobo_team["cug"].map(TEAM_MEMBERS)
    
    if kobo_team.empty:
        st.warning("No data found for the specified team members in this file.")
        st.stop()

    st.markdown('<div class="section-title">🏆 Overall Team Performance</div>', unsafe_allow_html=True)
    
    # Calculate performance metrics
    today = today_dt
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    
    # Build summary stats
    team_stats = []
    for cug, name in TEAM_MEMBERS.items():
        installer_data = kobo_team[kobo_team["cug"] == cug]
        all_time = len(installer_data)
        this_month = len(installer_data[installer_data["date"] >= start_of_month])
        this_week = len(installer_data[installer_data["date"] >= start_of_week])
        today_installs = len(installer_data[installer_data["date"] == today])
        
        team_stats.append({
            "Team Name": name,
            "CUG": cug,
            "Today's Installations": today_installs,
            "This Week's Installations": this_week,
            "This Month's Installations": this_month,
            "All Time Installations": all_time
        })
        
    stats_df = pd.DataFrame(team_stats).sort_values("All Time Installations", ascending=False)
    
    # Team Totals
    t_today = stats_df["Today's Installations"].sum()
    t_week = stats_df["This Week's Installations"].sum()
    t_month = stats_df["This Month's Installations"].sum()
    t_all = stats_df["All Time Installations"].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Today's Total", t_today)
    c2.metric("This Week's Total", t_week)
    c3.metric("This Month's Total", t_month)
    c4.metric("All Time Total", t_all)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    st.markdown('<div class="section-title">🔍 Installer Drill-Down</div>', unsafe_allow_html=True)
    
    # Selectbox for installer
    installer_options = [f"{row['Team Name']} (CUG: {row['CUG']})" for _, row in stats_df.iterrows()]
    selected_option = st.selectbox("Select Installer to Drill Down", installer_options)
    
    # Extract CUG from selection
    selected_cug = selected_option.split("CUG: ")[1].strip(")")
    selected_name = TEAM_MEMBERS[selected_cug]
    
    st.markdown(f"### {selected_name} - CUG: {selected_cug}")
    
    # Filter for the drill-down
    col1, col2 = st.columns([1, 4])
    with col1:
        time_filter = st.radio("Filter Installations:", ["Today", "This week", "This month"], index=2)
    
    with col2:
        installer_df = kobo_team[kobo_team["cug"] == selected_cug].copy()
        
        if time_filter == "Today":
            filtered_df = installer_df[installer_df["date"] == today]
        elif time_filter == "This week":
            filtered_df = installer_df[installer_df["date"] >= start_of_week]
        else: # This month
            filtered_df = installer_df[installer_df["date"] >= start_of_month]
            
        count = len(filtered_df)
        time_label = time_filter.lower()
        st.markdown(f"**{count} installation{'s' if count != 1 else ''} {time_label}**")
        
        if filtered_df.empty:
            st.info(f"No installations found for {selected_name} for {time_filter.lower()}.")
        else:
            disp_df = filtered_df.rename(columns={
                "phone": "Correct Customer Phone Number",
                "area": "Area of Installation",
                "imei": "IIMEI Number",
                "odu": "ODU Number",
                "date": "Submission Date"
            })
            st.dataframe(
                disp_df[["Correct Customer Phone Number", "Area of Installation", "IIMEI Number", "ODU Number", "Submission Date"]],
                use_container_width=True, 
                hide_index=True
            )

# ── DEVICE MANAGEMENT (Reconciliation) ─────────────────────────────────────────
elif app_mode == "Device Management":
    with st.sidebar:
        st.header("🗓 Date Filter (Device Mgt)")
        filter_mode = st.radio("Show data for:", ["Today", "This week", "Custom range"], index=1)
        if filter_mode == "Today":
            date_from = date_to = today_dt
        elif filter_mode == "This week":
            date_from = today_dt - timedelta(days=today_dt.weekday())
            date_to   = today_dt
        else:
            date_from = st.date_input("From", today_dt - timedelta(days=7))
            date_to   = st.date_input("To",   today_dt)

    if not kobo_file and not signout_file:
        st.markdown("""
        ### How to use Device Management
        **Step 1 — Kobo file:** KoboToolbox → Data → Downloads → **XLS** → open in Excel → Save As → **.xlsx** → upload here.

        **Step 2 — Sign-out file:** Google Sheet → File → Download → **.xlsx** → upload here.

        **Step 3:** Set the date filter. Report is ready instantly.

        ---
        > You can upload **just the Kobo file** to browse installations without reconciliation.
        """)
        st.stop()

    # ── KOBO ONLY ──
    if kobo_file and not signout_file:
        st.info("Showing **installations only**. Upload the sign-out file too to enable reconciliation.", icon="ℹ️")
        kobo = load_kobo(kobo_file)

        if debug:
            if kobo is not None:
                st.success(f"✅ Kobo loaded: {len(kobo)} rows")
                st.write("**Column names found:**", list(kobo.columns))
                st.dataframe(kobo.head(3))
            else:
                st.warning("Kobo returned None — see error above.")

        if kobo is None:
            st.stop()

        kobo_f = filter_by_date(kobo, date_from, date_to)

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

    # ── SIGN-OUT ONLY ──
    if signout_file and not kobo_file:
        signout = None
        df = read_file(signout_file)
        detected = detect_file_type(df) if df is not None else None

        if detected == "kobo":
            st.warning("This upload looks like a Kobo export. Showing Kobo installations instead.")
            kobo = load_kobo(signout_file)
            if kobo is None: st.stop()
            kobo_f = filter_by_date(kobo, date_from, date_to)
            
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
            st.stop()

        st.info("Showing **sign-out data only**. Upload the Kobo file to reconcile installations.", icon="ℹ️")
        signout = load_signout(signout_file)

        if debug:
            if signout is not None:
                st.success(f"✅ Sign-out loaded: {len(signout)} rows")
            else:
                st.warning("Sign-out returned None — see error above.")

        if signout is None: st.stop()

        signout_f = filter_by_date(signout, date_from, date_to)

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
        st.stop()

    # ── FULL MODE ──
    if kobo_file and signout_file:
        kobo    = load_kobo(kobo_file)
        signout = load_signout(signout_file)

        if kobo is None or signout is None:
            st.stop()

        kobo_f    = filter_by_date(kobo, date_from, date_to)
        signout_f = filter_by_date(signout, date_from, date_to)

        if kobo_f.empty and signout_f.empty:
            st.warning(f"No data found between {date_from} and {date_to}. Try changing the date filter.")
            st.stop()

        merged = signout_f.merge(
            kobo_f[["imei","phone","area","odu","date"]].rename(columns={"date":"install_date"}),
            on="imei", how="left"
        )
        merged["status"]             = merged["install_date"].apply(
            lambda x: "✅ Installed" if pd.notna(x) else "⚠️ Not installed")
        merged["days_since_signout"] = merged["date"].apply(lambda d: days_ago(d, today_dt))

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
