import streamlit as st
from src.ui.pdf_exports import dataframe_to_pdf
import os, glob, json, re
from src.database.connection import get_connection
import pandas as pd

st.set_page_config(layout="wide")
st.title("🛡️ Data Quality Report")
st.caption("Built from cleaning log + live validation checks: missing values, duplicates removed, unknown models, invalid dates, orphan records.")



@st.cache_data(ttl="5m", max_entries=2, show_spinner=False)
def read_cleaning_log():
    log_text=""; issues=[]
    for p in ["logs/cleaning_log.json","data/cleaning_log.json","logs/cleaning.log","data/cleaning.log"] + glob.glob("**/*clean*.log", recursive=True):
        if os.path.exists(p):
            try:
                with open(p,'r',encoding='utf-8',errors='ignore') as f:
                    txt=f.read(); log_text+=f"\n--- {p} ---\n{txt[:5000]}"
            except: pass
    return log_text, issues

@st.cache_data(ttl="5m", max_entries=2, show_spinner="Checking data quality...")
def run_live_checks():
    con = get_connection(read_only=True)
    tables=[t[0] for t in con.execute("SHOW TABLES").fetchall()]
    results=[]
    def add(table,issue,count,total,impact):
        share=(count/total*100) if total else 0
        results.append({"table":table,"issue":issue,"count":int(count),"total_rows":int(total),"share_pct":round(share,2),"impact":impact})
    primary_keys = {
        "branches": "branch_id", "models": "model_id", "salespeople": "salesperson_id",
        "inventory": "inventory_id", "sales": "sale_id", "service_records": "service_id",
        "warranty_claims": "claim_id", "complaints": "complaint_id", "satisfaction": "survey_id",
    }
    for t in tables:
        try:
            total=con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] or 0
            if total==0: continue
            cols=[c[0] for c in con.execute(f"DESCRIBE {t}").fetchall()]
            col_low=[c.lower() for c in cols]
            null_sql = "SELECT " + ", ".join(
                f'COUNT(*) FILTER (WHERE "{c}" IS NULL)' for c in cols
            ) + f' FROM "{t}"'
            null_counts = con.execute(null_sql).fetchone()
            for c, miss in zip(cols, null_counts):
                if miss > 0:
                    add(t,f"Missing values in {c}",miss,total,f"Affects KPIs if {c} is revenue/date. Analyses filtering on {c} will undercount [EV-001].")
            primary_key = primary_keys.get(t.lower())
            if primary_key and primary_key in cols:
                dup = con.execute(
                    f'SELECT COUNT(*) - COUNT(DISTINCT "{primary_key}") FROM "{t}"'
                ).fetchone()[0]
                if dup > 0:
                    add(t,"Duplicate primary keys",dup,total,"Can inflate counts and financial totals if not resolved.")
            if "model" in col_low:
                mc=cols[col_low.index("model")]
                try:
                    unk=con.execute(f"SELECT COUNT(*) FROM {t} WHERE LOWER({mc}) IN ('unknown','unk','n/a','na','') OR {mc} IS NULL").fetchone()[0]
                    if unk>0: add(t,f"Unknown models in {mc}",unk,total,"Affects Product / Inventory conclusions. Model breakdown will be inaccurate.")
                except: pass
            for dc in [c for c in cols if 'date' in c.lower()]:
                try:
                    inv=con.execute(f"SELECT COUNT(*) FROM {t} WHERE {dc}::DATE > CURRENT_DATE OR {dc}::DATE < '2000-01-01'").fetchone()[0]
                    if inv>0: add(t,f"Invalid dates in {dc}",inv,total,"Affects monthly revenue trends, June drop analysis, and Management Brief period filter [EV-005].")
                except:
                    try:
                        inv=con.execute(f"SELECT COUNT(*) FROM {t} WHERE TRY_CAST({dc} AS DATE) IS NULL AND {dc} IS NOT NULL").fetchone()[0]
                        if inv>0: add(t,f"Unparsable dates in {dc}",inv,total,"Breaks time-series. Rows excluded from period KPIs.")
                    except: pass
            if t.lower()=="sales":
                if "branches" in [x.lower() for x in tables]:
                    try:
                        orph=con.execute("SELECT COUNT(*) FROM sales s LEFT JOIN branches b ON s.branch_id=b.branch_id WHERE b.branch_id IS NULL").fetchone()[0]
                        if orph>0: add(t,"Orphan records: branch_id not in branches",orph,total,"Branch performance conclusions (best branch) will be incomplete [EV-004].")
                    except: pass
        except Exception as e:
            results.append({"table":t,"issue":f"Check failed: {e}","count":0,"total_rows":0,"share_pct":0,"impact":"Needs manual review"})
    return results

log_text, log_issues = read_cleaning_log()
checks = run_live_checks()

if checks:
    df=pd.DataFrame(checks)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Issues Found",len(df)); c2.metric("Tables Affected",df['table'].nunique())
    c3.metric("Total Affected",f"{df['count'].sum():,}"); worst=df.sort_values('share_pct',ascending=False).iloc[0]; c4.metric("Highest Share",f"{worst['share_pct']}%",help=f"Highest affected table: {worst['table']}")
    st.divider()
    st.subheader("Validation Checks")
    st.dataframe(df[["table","issue","count","total_rows","share_pct","impact"]].rename(columns={"share_pct":"share_%_of_table","impact":"which_conclusions_it_might_affect"}), width="stretch")
    detail_rows = df.sort_values(["share_pct", "count"], ascending=False).head(25)
    st.caption(
        f"Showing detailed expanders for the {len(detail_rows)} highest-impact checks; "
        "the table and downloads contain all checks."
    )
    for _,row in detail_rows.iterrows():
        with st.expander(f"{row['table']} — {row['issue']} — {row['count']} rows ({row['share_pct']}%)"):
            col1,col2=st.columns([1,2])
            with col1: st.metric("Count",row['count']); st.metric("Share",f"{row['share_pct']}%"); st.metric("Total Rows",row['total_rows'])
            with col2: st.warning(f"**Impact:** {row['impact']}"); st.progress(min(row['share_pct']/100,1.0), text=f"{row['share_pct']}% affected")
    st.download_button("📥 Download CSV", df.to_csv(index=False).encode(), "data_quality_report.csv", "text/csv", width="stretch")
    st.download_button(
        "Download PDF", dataframe_to_pdf("VersalMotors data quality report", df),
        "data_quality_report.pdf", "application/pdf", width="stretch",
        icon=":material/picture_as_pdf:",
    )
else:
    st.success("No issues - all checks passed!")

st.divider(); st.subheader("Cleaning Log (Raw)")
if log_text: st.code(log_text[:10000])
else: st.info("No cleaning log file found - showing live checks only (acceptable).")
