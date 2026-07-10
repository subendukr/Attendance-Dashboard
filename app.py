import streamlit as st

from pathlib import Path

from auth.session import initialize_session, is_logged_in

from auth.navigation import create_navigation

from auth.ui import render_login


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Neelkamal Attendance Dashboard", page_icon="🏭", layout="wide"
)


# ==========================================================
# LOAD GLOBAL CSS
# ==========================================================


def load_css():

    css = Path("styles/style.css")

    if css.exists():
        st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)


load_css()


# ==========================================================
# INITIALIZE SESSION
# ==========================================================

initialize_session()


# ==========================================================
# LOGIN
# ==========================================================

if not is_logged_in():
    render_login()

    st.stop()


# ==========================================================
# APPLICATION
# ==========================================================

navigation = create_navigation()

navigation.run()
