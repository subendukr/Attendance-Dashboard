"""
Authorization & Permission Management

Uses the authenticated user's role together with
config/roles.json to determine page and feature access.
"""

import streamlit as st

from auth.config import has_permission
from auth.session import current_role, is_logged_in


# ==========================================================
# REQUIRE LOGIN
# ==========================================================


def require_login():
    """
    Ensure the user is authenticated.
    """

    if not is_logged_in():
        st.warning("Please sign in to continue.")

        st.stop()


# ==========================================================
# CHECK PERMISSION
# ==========================================================


def can(permission):
    """
    Check whether the current user has
    a specific permission.

    Parameters
    ----------
    permission : str

    Returns
    -------
    bool
    """

    if not is_logged_in():
        return False

    role = current_role()

    return has_permission(role, permission)


# ==========================================================
# REQUIRE PERMISSION
# ==========================================================


def require_permission(permission):
    """
    Stop execution if the current user
    lacks the required permission.
    """

    require_login()

    if not can(permission):
        st.error("⛔ Access Denied\n\nYou do not have permission to access this page.")

        st.stop()


# ==========================================================
# ROLE HELPERS
# ==========================================================


def is_admin():

    return current_role() == "Admin"


def is_hr():

    return current_role() == "HR"


def is_gm():

    return current_role() == "GM"


def is_director():

    return current_role() == "Director"
