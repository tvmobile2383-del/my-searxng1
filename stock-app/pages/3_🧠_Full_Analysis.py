import streamlit as st
from modules.stock_data import get_snapshot
from modules.analysis_engine import collect_company_evidence, make_prompt, run_qwen_analysis
from modules.ui import render_sidebar

st.set_page_config(page_title="Full AE8 AE11 Analysis", page_icon="🧠", layout="wide")
st.title("🧠 Full AE8 / AE11 Analysis")
render_sidebar()

symbols = list(st.session_state.selected_stocks)
if not symbols:
    st.info("Add stocks to your shortlist first.")
    st.stop()

chosen = st.multiselect("Choose stocks to analyse", symbols, default=symbols[:1])
st.caption("Each selected stock is analysed sequentially. Keep your Qwen Kaggle API and Cloudflare tunnel online.")
if st.button("Run full analysis", type="primary", disabled=not chosen):
    for symbol in chosen:
        with st.status(f"Analysing {symbol}...", expanded=True) as status:
            try:
                st.write("Fetching market and financial snapshot...")
                snapshot = get_snapshot(symbol)
                st.write("Searching company results, annual reports and growth plans...")
                evidence = collect_company_evidence(snapshot["company"], symbol)
                prompt = make_prompt(snapshot, evidence)
                st.write("Sending evidence pack to Qwen...")
                report = run_qwen_analysis(prompt, snapshot)
                st.session_state.analysis_results[symbol] = {
                    "symbol": symbol, "company": snapshot["company"],
                    "snapshot": snapshot, "evidence": evidence, "report": report
                }
                status.update(label=f"{symbol}: analysis complete", state="complete")
            except Exception as exc:
                status.update(label=f"{symbol}: analysis failed", state="error")
                st.error(f"{symbol}: {exc}")

if st.session_state.analysis_results:
    st.divider()
    for symbol, result in st.session_state.analysis_results.items():
        with st.expander(f"{result.get('company', symbol)} ({symbol})", expanded=True):
            st.markdown(result["report"])
            with st.expander("Market snapshot and source evidence"):
                st.json(result["snapshot"])
                for item in result.get("evidence", []):
                    if item.get("url"):
                        st.markdown(f"- [{item.get('title') or item['url']}]({item['url']}) — {item.get('content','')}")
