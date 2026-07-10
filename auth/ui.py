"""
Authentication User Interface
"""

import streamlit as st

from auth.users import authenticate_user
from auth.session import login, current_name, current_role, current_user


# ==========================================================
# LOGIN FORM
# ==========================================================


def render_login():

    left, center, right = st.columns([1, 2, 1])

    with center:
        st.markdown(
            """
            <div style="text-align:center;padding-top:40px;">
                <h1>Neelkamal Steel Industry</h1>
                <h3>Attendance Management Dashboard</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")

            password = st.text_input("Password", type="password")

            st.caption("Press **Enter** after entering your password to login.")

            submitted = st.form_submit_button("Sign In", width="stretch")

            if submitted:
                if not username.strip():
                    st.error("Please enter your username.")

                    return

                if not password:
                    st.error("Please enter your password.")

                    return

                user = authenticate_user(username, password)

                if user is None:
                    st.error("Invalid username or password.")

                    return

                login(user)

                st.success(f"Welcome {user['Name']}")

                st.rerun()


# ==========================================================
# AUTHENTICATION STATUS
# ==========================================================


def render_auth_status():

    st.success("Successfully Signed In")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("User", current_user())

    with col2:
        st.metric("Name", current_name())

    with col3:
        st.metric("Role", current_role())

    st.info("Navigation will be added in the next step.")
