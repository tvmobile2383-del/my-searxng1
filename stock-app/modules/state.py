import streamlit as st

def init_state():
    defaults = {
        "selected_stocks": {},
        "analysis_results": {},
        "result_search": [],
        "screen_results": None,
        "screen_errors": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
