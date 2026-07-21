"""
Application Navigation

Creates the application sidebar and
role-based page navigation.
"""

import streamlit as st

from auth.permissions import can

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

PAGE_CONFIG = [
    {
        "permission": "dashboard",
        "path": "pages/1_Dashboard.py",
        "title": "Dashboard",
        "subtitle": "Employee Attendance Dashboard",
        "icon": "📊",
    },
    {
        "permission": "employee_search",
        "path": "pages/2_Employee_Search.py",
        "title": "Employee Search",
        "subtitle": "Employee Search",
        "icon": "👤",
    },
    {
        "permission": "analytics",
        "path": "pages/3_Analytics.py",
        "title": "Analytics",
        "subtitle": "Attendance Analytics",
        "icon": "📈",
    },
    {
        "permission": "upload",
        "path": "pages/4_Upload.py",
        "title": "Upload",
        "subtitle": "Attendance Data Upload",
        "icon": "📁",
    },
]

# ==========================================================
# BUILD PAGE LIST
# ==========================================================


def build_pages():

    pages = []

    for page in PAGE_CONFIG:
        if can(page["permission"]):
            pages.append(st.Page(page["path"], title=page["title"], icon=page["icon"]))

    return pages


# ==========================================================
# CREATE NAVIGATION
# ==========================================================


def create_navigation():

    pages = build_pages()

    navigation = st.navigation(pages)

    return navigation
