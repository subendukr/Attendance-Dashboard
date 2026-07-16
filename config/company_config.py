"""
Company Configuration

Loads company definitions from companies.json
and provides helper functions for the application.
"""

from utils.repository import (
    load_companies as repository_load_companies,
    save_companies as repository_save_companies,
)

# ==========================================================
# LOAD CONFIGURATION
# ==========================================================


def load_companies():

    data = repository_load_companies()

    return data.get(
        "companies",
        {},
    )


# ==========================================================
# GET ALL COMPANIES
# ==========================================================


def company_list():

    companies = load_companies()

    return [company["name"] for company in companies.values()]


# ==========================================================
# GET COMPANY DETAILS
# ==========================================================


def company_details(code):

    companies = load_companies()

    return companies.get(code.upper())


# ==========================================================
# GET COMPANY NAME
# ==========================================================


def company_name(code):

    details = company_details(code)

    if details:
        return details["name"]

    return None

# ==========================================================
# SAVE COMPANY NAME
# ==========================================================

def save_companies(companies):

    repository_save_companies(
        {
            "companies": companies,
        }
    )