import streamlit as st
import pandas as pd
from datetime import date, timedelta
from src.ai.brief import get_kpis_for_period, build_evidence, generate_brief_sections

st.set_page_config(layout="wide")
st.title("📋 Management Brief")

# --- Period selector - mobile friendly ---
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=date(2024,1,1))
with col2:
    end_date = st.date_input("End Date", value=date(2024,12,31))

if st.button("🚀 Generate Brief", type="primary", use_container_width=True):
    with st.spinner("Building brief with evidence..."):
        kpis = get_kpis_for_period(str(start_date), str(end_date))
        evidence = build_evidence(kpis, str(start_date), str(end_date))
        brief = generate_brief_sections(kpis, evidence, str(start_date), str(end_date))

        # --- DISPLAY BRIEF - mobile readable ---
        if "raw" in brief: # AI version
            st.markdown(brief["raw"])
        else:
            with st.container(border=True):
                st.subheader("Executive Summary")
                st.write(brief["executive_summary"])

            with st.container(border=True):
                st.subheader("Key Findings")
                st.markdown(brief["key_findings"])

            with st.container(border=True):
                st.subheader("Areas Requiring Attention")
                st.markdown(brief["areas_attention"])

            with st.container(border=True):
                st.subheader("Opportunities")
                st.markdown(brief["opportunities"])

            with st.container(border=True):
                st.subheader("Recommended Actions")
                st.markdown(brief["recommended_actions"])

            with st.container(border=True):
                st.subheader("Questions Requiring Further Investigation")
                st.markdown(brief["questions"])

        # --- SUPPORTING EVIDENCE TABLE (Required) ---
        st.divider()
        st.subheader("Supporting Evidence")
        ev_df = pd.DataFrame([{"Evidence ID": e["id"], "Description": e["label"], "Value": e["value"]} for e in evidence])
        st.dataframe(ev_df, use_container_width=True)

        # Detail expanders to trace claim -> source data -> number (For Check)
        for e in evidence:
            with st.expander(f"{e['id']}: {e['label']} = {e['value']}"):
                st.dataframe(e["df"], use_container_width=True)
                st.caption(f"Number {e['number']} traced and verified against source data")

        # --- EXPORT MARKDOWN AND PDF (Required) ---
        md_content = f"""# Management Brief {start_date} to {end_date}

## Executive Summary
{brief.get('executive_summary', brief.get('raw',''))}

## Key Findings
{brief.get('key_findings','')}

## Areas Requiring Attention
{brief.get('areas_attention','')}

## Opportunities
{brief.get('opportunities','')}

## Supporting Evidence
{ev_df.to_markdown(index=False)}

## Recommended Actions
{brief.get('recommended_actions','')}

## Questions Requiring Further Investigation
{brief.get('questions','')}
"""
        st.download_button("📥 Export Markdown", md_content.encode(), f"brief_{start_date}_{end_date}.md", "text/markdown", use_container_width=True)

        # Simple PDF export via markdown as txt - works without extra libs
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=11)
            for line in md_content.split("\n"):
                pdf.multi_cell(0, 8, line.encode('latin-1','ignore').decode('latin-1'))
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("📄 Export PDF", pdf_bytes, f"brief_{start_date}_{end_date}.pdf", "application/pdf", use_container_width=True)
        except:
            st.download_button("📄 Export PDF (as TXT)", md_content.encode(), f"brief_{start_date}_{end_date}.pdf", "application/pdf", use_container_width=True)


else:
    st.info("Select period and click Generate Brief")
