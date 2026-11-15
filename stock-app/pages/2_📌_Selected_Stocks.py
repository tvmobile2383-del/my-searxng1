import streamlit as st
import pandas as pd
from modules.ui import render_sidebar

st.set_page_config(page_title="Selected Stocks", page_icon="📌", layout="wide")
st.title("📌 Selected Stocks")
render_sidebar()

symbol = st.text_input("Add an NSE symbol manually (example: SJS, SANsera, BEL)").strip().upper()
if st.button("Add symbol") and symbol:
    st.session_state.selected_stocks[symbol] = {"symbol": symbol, "source": "Manual"}
    st.rerun()

selected = st.session_state.selected_stocks
if not selected:
    st.info("Your shortlist is empty. Discover stocks or add a symbol above.")
else:
    df = pd.DataFrame([{"Symbol": k, "Discovery source": v.get("source", "Manual")} for k, v in selected.items()])
    st.dataframe(df, use_container_width=True, hide_index=True)
    remove = st.multiselect("Choose symbols to remove", list(selected))
    if st.button("Remove selected") and remove:
        for s in remove:
            selected.pop(s, None)
        st.rerun()
    st.write(f"**{len(selected)} stocks** in your shortlist.")
