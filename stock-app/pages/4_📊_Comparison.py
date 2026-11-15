import streamlit as st
import pandas as pd
from modules.ui import render_sidebar

st.set_page_config(page_title="Analysis Comparison", page_icon="📊", layout="wide")
st.title("📊 Analysis Comparison")
render_sidebar()

results = st.session_state.analysis_results
if not results:
    st.info("No completed analyses yet. Run analysis from the Full Analysis page.")
    st.stop()

rows = []
for symbol, item in results.items():
    snap = item.get("snapshot", {})
    rows.append({
        "Symbol": symbol, "Company": item.get("company"),
        "Sector": snap.get("sector"),
        "Market cap ₹ Cr": round(snap["market_cap_crore"], 1) if snap.get("market_cap_crore") else None,
        "PE": snap.get("trailing_pe"),
        "ROE %": round(snap["roe"] * 100, 1) if snap.get("roe") is not None else None,
        "Revenue growth %": round(snap["revenue_growth"] * 100, 1) if snap.get("revenue_growth") is not None else None,
        "Earnings growth %": round(snap["earnings_growth"] * 100, 1) if snap.get("earnings_growth") is not None else None,
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

for symbol, item in results.items():
    with st.expander(f"Read {item.get('company', symbol)} report"):
        st.markdown(item.get("report", ""))
