import streamlit as st

from utils.repository import (
    load_users,
    load_roles,
    load_companies,
    load_metadata,
    load_daily,
    load_monthly,
)

# -------------------------------------------------
# Cache durations (seconds)
# -------------------------------------------------

CACHE_SHORT = 60
CACHE_MEDIUM = 300
CACHE_LONG = 3600


@st.cache_data(ttl=CACHE_LONG)
def get_users():
    return load_users()


@st.cache_data(ttl=CACHE_LONG)
def get_roles():
    return load_roles()


@st.cache_data(ttl=CACHE_LONG)
def get_companies():
    return load_companies()


@st.cache_data(ttl=CACHE_SHORT)
def get_metadata():
    return load_metadata()


@st.cache_data(ttl=CACHE_MEDIUM)
def get_daily():
    return load_daily()


@st.cache_data(ttl=CACHE_MEDIUM)
def get_monthly():
    return load_monthly()


def clear_cache():
    """
    Clear every cached dataset.
    """
    st.cache_data.clear()