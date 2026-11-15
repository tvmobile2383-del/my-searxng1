import streamlit as st
from modules.config import SEARXNG_URL, STOCK_API_URL

def render_sidebar():
    with st.sidebar:
        st.markdown("## Service status")
        st.write("SearXNG:", "🟢 URL configured" if SEARXNG_URL else "🟠 URL missing")
        st.write("Qwen API:", "🟢 URL configured" if STOCK_API_URL else "🟠 URL missing")
        st.caption("For Qwen analysis, the Kaggle runtime and Cloudflare tunnel must remain active.")
