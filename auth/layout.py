"""
Application Layout

Shared layout components used across the
Attendance Dashboard.
"""

from datetime import datetime

import streamlit as st

from auth.session import current_name, current_role, current_company, logout

from config.company_config import company_details

# ==========================================================
# USER INITIALS
# ==========================================================


def get_initials():
    """
    Generate initials from the logged-in user's name.
    """

    name = current_name() or ""

    parts = [p.strip() for p in name.split() if p.strip()]

    if not parts:
        return "?"

    if len(parts) == 1:
        return parts[0][0].upper()

    return (parts[0][0] + parts[-1][0]).upper()


# ==========================================================
# CURRENT DATE & TIME
# ==========================================================


def current_datetime():

    return datetime.now().strftime("%d %b %Y • %I:%M %p")


# ==========================================================
# CURRENT COMPANY NAME
# ==========================================================


def current_company_name():
    """
    Return the display name of the logged-in user's company.
    """

    company_code = current_company()

    if not company_code:
        return "Unknown"

    if company_code == "ALL":
        return "All Companies"

    company = company_details(company_code)

    if company:
        return company["name"]

    return company_code


# ==========================================================
# HEADER
# ==========================================================


def render_header(title: str, subtitle: str):
    """
    Render executive user card.
    """

    left, right = st.columns([7.5, 2.5], vertical_alignment="center")

    with left:
        st.markdown(
            f"""
    <div style="padding-top:8px;">

    <h1 style="
    margin-bottom:0;
    color:#F8FAFC;
    ">

    {title}

    <div style="font-size:34px;">

    <p style="
    font-size:22px;
    color:#CBD5E1;
    margin-top:4px;
    margin-bottom:0;
    font-weight:500;
    ">

    {subtitle}

    <div style="font-size:20px;">

    </div>
    """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
    <div style="
    background:#1F2937;
    border:1px solid #374151;
    border-radius:14px;
    padding:14px 16px;
    box-shadow:0 2px 8px rgba(0,0,0,.20);
    ">

    <div style="
    display:flex;
    align-items:center;
    ">

    <div style="
    width:52px;
    height:52px;
    border-radius:50%;
    background:#1D4ED8;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
    font-weight:700;
    color:white;
    margin-right:14px;
    flex-shrink:0;
    ">

    {get_initials()}

    </div>

    <div>

    <div style="
    font-size:18px;
    font-weight:700;
    color:white;
    ">

    {current_name()}

    </div>

    <div style="
    margin-top:4px;
    font-size:13px;
    color:#94A3B8;
    ">

    🛡 {current_role()}

    </div>

    <div style="
    margin-top:4px;
    font-size:13px;
    color:#CBD5E1;
    ">

    🏭 {current_company_name()}

    </div>

    <div style="
    margin-top:6px;
    font-size:12px;
    color:#22C55E;
    ">

    🟢 Online

    </div>

    <div style="
    margin-top:6px;
    font-size:12px;
    color:#CBD5E1;
    ">

    🕒 {datetime.now()}

    </div>

    </div>

    </div>

    </div>
    """,
            unsafe_allow_html=True,
        )

        if st.button("🚪 Logout", key="header_logout", width="stretch"):
            logout()

            st.rerun()

    st.divider()
