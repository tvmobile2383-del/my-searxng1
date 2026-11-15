import streamlit as st
import pandas as pd
from modules.search import search_web, result_search_queries
from modules.stock_data import run_screen
from modules.universe import STARTER_SYMBOLS
from modules.ui import render_sidebar
if "result_search" not in st.session_state:
    st.session_state.result_search = []
    
st.set_page_config(page_title="Discover Stocks", page_icon="🔎", layout="wide")
st.title("🔎 Discover Indian Stocks")
render_sidebar()

st.subheader("A. Results announcement discovery")
period = st.selectbox("Search period", ["Today", "Last 3 days", "Last 7 days"])
if st.button("Search result announcements", type="primary"):
    gathered = []
    with st.spinner("Searching SearXNG..."):
        try:
            for query in result_search_queries(period):
                gathered.extend(search_web(query, 10))
            dedup, seen = [], set()
            for item in gathered:
                url = item.get("url", "")
                if url and url not in seen:
                    dedup.append(item); seen.add(url)
            st.session_state.result_search = dedup
            st.success(f"Found {len(dedup)} unique search results.")
        except Exception as exc:
            st.error(f"Search failed: {exc}")

for item in st.session_state.result_search:
    with st.container(border=True):
        st.markdown(f"**{item.get('title') or 'Search result'}**")
        st.write(item.get("content", ""))
        if item.get("url"):
            st.markdown(f"[Open source]({item['url']})")
        if item.get("publishedDate"):
            st.caption(f"Published: {item['publishedDate']}")

if st.session_state.result_search:
    st.caption("Search results identify possible announcements; they do not prove that a company has declared results. Verify the exchange filing.")
    symbol = st.text_input("Enter the NSE symbol mentioned in a result (example: SJS)", key="result_symbol").strip().upper()
    if st.button("Add result company to shortlist") and symbol:
        st.session_state.selected_stocks[symbol] = {"symbol": symbol, "source": "Results announcement search"}
        st.success(f"{symbol} added to shortlist.")

st.divider()
st.subheader("B. Fundamental screening")
st.caption("The starter universe is not the full NSE/BSE universe. Upload a CSV with a `symbol` column to add symbols.")
uploaded = st.file_uploader("Optional NSE symbol CSV", type=["csv"])
symbols = list(STARTER_SYMBOLS)
if uploaded:
    try:
        df = pd.read_csv(uploaded)
        col = "symbol" if "symbol" in df.columns else df.columns[0]
        symbols = list(dict.fromkeys(symbols + df[col].dropna().astype(str).str.upper().tolist()))
        st.success(f"Universe contains {len(symbols)} symbols.")
    except Exception as exc:
        st.error(f"CSV read error: {exc}")

x, y, z = st.columns(3)
min_cap = x.number_input("Minimum market cap (₹ Cr)", min_value=0, value=1000, step=1000)
min_rev = y.number_input("Minimum revenue growth (%)", min_value=-100, max_value=500, value=0)
min_roe = z.number_input("Minimum ROE (%)", min_value=-100, max_value=200, value=0)
scan_count = st.slider("Symbols to scan per run", 10, min(100, len(symbols)), min(30, len(symbols)), 5)

if st.button("Run fundamental screen"):
    with st.spinner(f"Fetching {scan_count} symbols. This may take several minutes..."):
        results, errors = run_screen(symbols[:scan_count], min_cap, min_rev / 100, min_roe / 100)
        st.session_state.screen_results = results
        st.session_state.screen_errors = errors

results = st.session_state.screen_results
if results is not None:
    if results.empty:
        st.warning("No stocks matched, or data was unavailable. Try lowering filters or scanning more symbols.")
    else:
        st.dataframe(results, use_container_width=True, hide_index=True)
        chosen = st.multiselect("Select stocks to shortlist", results["Symbol"].tolist())
        if st.button("Add selected screened stocks"):
            for s in chosen:
                st.session_state.selected_stocks[s] = {"symbol": s, "source": "Fundamental screen"}
            st.success(f"Added {len(chosen)} stocks.")
if st.session_state.screen_errors:
    with st.expander(f"Data retrieval errors ({len(st.session_state.screen_errors)})"):
        st.write(st.session_state.screen_errors)
