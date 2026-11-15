import streamlit as st
from modules.state import init_state
from modules.ui import render_sidebar

st.set_page_config(page_title="India Stock Discovery & Analysis", page_icon="📈", layout="wide")
init_state()
st.title("🇮🇳 India Stock Discovery & AI Analysis")
st.caption("Discover Indian listed companies • Build a shortlist • Run full AE8 / AE11 research")
render_sidebar()

a, b, c = st.columns(3)
a.metric("Shortlisted stocks", len(st.session_state.selected_stocks))
b.metric("Completed analyses", len(st.session_state.analysis_results))
c.metric("Market", "NSE / BSE")

st.markdown("""
### Workflow
1. **Discover Stocks** — search for result announcements and run a fundamental screen.
2. **Selected Stocks** — maintain your shortlist.
3. **Full Analysis** — retrieve company context and ask your Qwen model for AE8 / AE11 analysis.
4. **Comparison** — compare completed reports.

Use the left navigation to get started.

**Data caution:** This first version uses SearXNG search results and Yahoo Finance via `yfinance`. Search snippets are discovery leads, not verified exchange filings. Financial data coverage and freshness vary. Confirm figures against NSE/BSE filings and company disclosures before making investment decisions.
""")
st.info("The Qwen analysis service must be running and reachable at STOCK_API_URL. Keep the Kaggle notebook and Cloudflare tunnel active while analysing.")
