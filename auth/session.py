"""
Session Management

Manages authenticated user information using
Streamlit session state.

This module is responsible only for session
management.
"""

import streamlit as st


# ==========================================================
# SESSION KEYS
# ==========================================================

SESSION_DEFAULTS = {
    "logged_in": False,
    "username": None,
    "name": None,
    "role": None,
    "company": None,
}


# ==========================================================
# INITIALIZE SESSION
# ==========================================================


def initialize_session():
    """
    Initialize authentication session variables.
    """

    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ==========================================================
# LOGIN
# ==========================================================


def login(user):
    """
    Store authenticated user in session.

    Parameters
    ----------
    user : pandas.Series
    """

    initialize_session()

    st.session_state.logged_in = True

    st.session_state.username = user["Username"]

    st.session_state.name = user["Name"]

    st.session_state.role = user["Role"]

    st.session_state.company = user["Company"]


# ==========================================================
# LOGOUT
# ==========================================================


def logout():
    """
    Clear authentication session.
    """

    initialize_session()

    st.session_state.logged_in = False

    st.session_state.username = None

    st.session_state.name = None

    st.session_state.role = None

    st.session_state.company = None


# ==========================================================
# LOGIN STATUS
# ==========================================================


def is_logged_in():
    """
    Return login status.
    """

    initialize_session()

    return st.session_state.logged_in


# ==========================================================
# CURRENT USER
# ==========================================================


def current_user():

    initialize_session()

    return st.session_state.username


# ==========================================================
# CURRENT NAME
# ==========================================================


def current_name():

    initialize_session()

    return st.session_state.name


# ==========================================================
# CURRENT ROLE
# ==========================================================


def current_role():

    initialize_session()

    return st.session_state.role


# ==========================================================
# CURRENT COMPANY
# ==========================================================


def current_company():
    """
    Return the logged-in user's company code.
    """

    initialize_session()

    return st.session_state.company


def current_user_context():
    """
    Return the complete session context.
    """

    initialize_session()

    return {
        "username": st.session_state.username,
        "name": st.session_state.name,
        "role": st.session_state.role,
        "company": st.session_state.company,
    }
