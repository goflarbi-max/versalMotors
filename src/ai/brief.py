"""
Step 5: Management Brief - src/ai/brief.py
Pull top insights and KPIs for selected period, generate brief with evidence ids.
Every finding must cite evidence ids.
"""
from src.database.connection import get_connection
import pandas as pd
from datetime import date
from typing import Dict, List, Tuple
import os, glob
from src.ai.gemini_client import generate_text

def get_kpis_for_period(start_date: str, end_date: str) -> Dict:
    con = get_connection(read_only=True)
    try:
        # Hardcode correct names instead of guessing to support parameterization
        rev_col = "total_sale_price"
        date_col = "sale_date"

        revenue = con.execute("SELECT SUM(total_sale_price) FROM sales WHERE sale_date BETWEEN ? AND ?", [start_date, end_date]).fetchone()[0] or 0
        sales = con.execute("SELECT COUNT(*) FROM sales WHERE sale_date BETWEEN ? AND ?", [start_date, end_date]).fetchone()[0] or 0
        avg_ticket = revenue / sales if sales else 0

        # branch performance
        branch_df = con.execute("""
            SELECT branch_id, SUM(total_sale_price) as rev, COUNT(*) as cnt
            FROM sales WHERE sale_date BETWEEN ? AND ?
            GROUP BY branch_id ORDER BY rev DESC
        """, [start_date, end_date]).fetchdf()

        # monthly trend
        monthly_df = con.execute("""
            SELECT DATE_TRUNC('month', sale_date)::DATE as month, SUM(total_sale_price) as rev
            FROM sales WHERE sale_date BETWEEN ? AND ?
            GROUP BY 1 ORDER BY 1
        """, [start_date, end_date]).fetchdf()

        # inventory low
        try:
            low_stock = con.execute("SELECT COUNT(*) FROM inventory WHERE quantity < 10").fetchone()[0]
        except:
            low_stock = 0

        return {
            "revenue": float(revenue),
            "sales": int(sales),
            "avg_ticket": float(avg_ticket),
            "branch_df": branch_df,
            "monthly_df": monthly_df,
            "low_stock": int(low_stock),
            "rev_col": rev_col,
            "date_col": date_col
        }
    except Exception as e:
        return {"revenue":0,"sales":0,"avg_ticket":0,"branch_df":pd.DataFrame(),"monthly_df":pd.DataFrame(),"low_stock":0,"error":str(e)}

def build_evidence(kpis: Dict, start_date: str, end_date: str) -> List[Dict]:
    """Build evidence table - every finding will cite these ids"""
    evidence = []
    evidence.append({
        "id": "EV-001",
        "label": "Total Revenue in Period",
        "value": f"GHS {kpis['revenue']:,.2f}",
        "number": kpis['revenue'],
        "sql": f"SELECT SUM({kpis.get('rev_col','total_sale_price')}) FROM sales WHERE {kpis.get('date_col','sale_date')} BETWEEN '{start_date}' AND '{end_date}'",
        "df": pd.DataFrame([{"metric":"Revenue","value":kpis['revenue']}])
    })
    evidence.append({
        "id": "EV-002",
        "label": "Total Sales Count",
        "value": f"{kpis['sales']:,}",
        "number": kpis['sales'],
        "sql": f"SELECT COUNT(*) FROM sales WHERE date BETWEEN '{start_date}' AND '{end_date}'",
        "df": pd.DataFrame([{"metric":"Sales","value":kpis['sales']}])
    })
    evidence.append({
        "id": "EV-003",
        "label": "Average Ticket Size",
        "value": f"GHS {kpis['avg_ticket']:,.2f}",
        "number": kpis['avg_ticket'],
        "sql": f"SELECT SUM(total_sale_price)/COUNT(*) FROM sales WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'",
        "df": pd.DataFrame([{"metric":"Avg Ticket","value":kpis['avg_ticket']}])
    })
    if not kpis['branch_df'].empty:
        top_branch = kpis['branch_df'].iloc[0]
        evidence.append({
            "id": "EV-004",
            "label": f"Top Branch {top_branch['branch_id']}",
            "value": f"GHS {top_branch['rev']:,.2f}",
            "number": float(top_branch['rev']),
            "sql": f"SELECT branch_id, SUM({kpis.get('rev_col')}) FROM sales GROUP BY branch_id ORDER BY 2 DESC",
            "df": kpis['branch_df'].head(3)
        })
    if not kpis['monthly_df'].empty:
        # find lowest month
        min_row = kpis['monthly_df'].loc[kpis['monthly_df']['rev'].idxmin()]
        evidence.append({
            "id": "EV-005",
            "label": f"Lowest Month {min_row['month']}",
            "value": f"GHS {min_row['rev']:,.2f}",
            "number": float(min_row['rev']),
            "sql": f"SELECT month, SUM(rev) FROM sales GROUP BY month ORDER BY rev",
            "df": kpis['monthly_df']
        })
    evidence.append({
        "id": "EV-006",
        "label": "Low Stock Alerts",
        "value": f"{kpis['low_stock']}",
        "number": kpis['low_stock'],
        "sql": "SELECT COUNT(*) FROM inventory WHERE quantity < 10",
        "df": pd.DataFrame([{"low_stock":kpis['low_stock']}])
    })
    return evidence

def generate_brief_sections(kpis: Dict, evidence: List[Dict], start_date: str, end_date: str) -> Dict[str, str]:
    """Generate brief - tries AI, falls back to deterministic with evidence ids"""
    try:
        key = os.getenv("GEMINI_API_KEY","")
        try:
            import streamlit as st
            key = st.secrets.get("GEMINI_API_KEY", key)
        except: pass
        if key:
            model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
            ev_text = "\n".join([f"{e['id']}: {e['label']} = {e['value']} | SQL: {e['sql']}" for e in evidence])
            prompt = f"""
            Period: {start_date} to {end_date}
            Evidence:
            {ev_text}
            KPIs: Revenue GHS {kpis['revenue']:.2f}, Sales {kpis['sales']}, Avg {kpis['avg_ticket']:.2f}

            Generate Management Brief with these EXACT headings, every finding MUST cite [EV-XXX] ids:

            EXECUTIVE SUMMARY:
            KEY FINDINGS: (3-5 bullets with [EV-XXX])
            AREAS REQUIRING ATTENTION: (with [EV-XXX])
            OPPORTUNITIES: (with [EV-XXX])
            RECOMMENDED ACTIONS:
            QUESTIONS REQUIRING FURTHER INVESTIGATION:
            """
            result = generate_text(prompt, api_key=key, model=model)
            if result["ok"]:
                return {"raw": result["text"], "evidence": evidence}
    except Exception as e:
        pass

    # Fallback deterministic - every finding cites evidence ids (REQUIRED)
    ev001, ev002 = evidence[0]['value'], evidence[1]['value']
    summary = f"Business generated {ev001} from {ev002} sales between {start_date} and {end_date} [EV-001][EV-002]."
    findings = f"""
    - Revenue in period was {evidence[0]['value']} [EV-001]
    - Total transactions were {evidence[1]['value']} [EV-002]
    - Average ticket size was {evidence[2]['value']} [EV-003]
    - Top performing branch drove {evidence[3]['value'] if len(evidence)>3 else 'majority'} of revenue [EV-004]
    - Lowest month recorded {evidence[4]['value'] if len(evidence)>4 else 'drop'} [EV-005]
    """
    attention = f"""
    - Low stock alerts at {evidence[-1]['value']} items need restock [EV-006]
    - Month with lowest revenue {evidence[4]['value'] if len(evidence)>4 else 'needs review'} shows seasonality risk [EV-005]
    """
    opportunities = f"""
    - Replicate top branch strategy [EV-004] across other branches to lift avg ticket [EV-003]
    - Upsell to increase ticket from {evidence[2]['value']} [EV-003]
    """
    return {
        "executive_summary": summary,
        "key_findings": findings,
        "areas_attention": attention,
        "opportunities": opportunities,
        "recommended_actions": "- Restock low inventory [EV-006]\n- Investigate low month [EV-005]\n- Coach low performing branches vs [EV-004]",
        "questions": "- Why did lowest month dip? [EV-005]\n- What drives top branch success? [EV-004]\n- Can we increase avg ticket above [EV-003]?",
        "evidence": evidence
    }
