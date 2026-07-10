"""
Centralized Data Access Layer

All pages should load attendance data through this
module instead of calling load_data.py directly.

This module will later provide:

• Company-based filtering
• Permission-aware datasets
• Caching
• Future row-level security
"""

from auth.session import current_company

from utils.load_data import load_daily, load_monthly

# ==========================================================
# APPLY COMPANY FILTER
# ==========================================================


def _apply_company_filter(df):
    """
    Filter a dataframe based on the logged-in user's company.

    Admin / MD / HR (Company = ALL)
    receive the complete dataset.

    Company users receive only
    their own company's records.
    """

    if df.empty:
        return df

    company = current_company()

    if not company:
        return df

    if company.upper() == "ALL":
        return df

    if "Company" not in df.columns:
        return df

    return df[df["Company"].str.upper() == company.upper()].copy()


# ==========================================================
# LOAD MONTHLY DATA
# ==========================================================


def load_monthly_data():
    """
    Return the monthly attendance dataset
    filtered for the current user.
    """

    monthly = load_monthly()

    return _apply_company_filter(monthly)


# ==========================================================
# LOAD DAILY DATA
# ==========================================================


def load_daily_data():
    """
    Return the daily attendance dataset
    filtered for the current user.
    """

    daily = load_daily()

    return _apply_company_filter(daily)
