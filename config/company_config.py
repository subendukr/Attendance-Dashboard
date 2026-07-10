"""
Company Configuration

Loads company definitions from companies.json
and provides helper functions for the application.
"""

from pathlib import Path
import json


# ==========================================================
# CONFIG FILE
# ==========================================================

COMPANY_FILE = Path("config/companies.json")


# ==========================================================
# LOAD CONFIGURATION
# ==========================================================


def load_companies():

    if not COMPANY_FILE.exists():
        raise FileNotFoundError(f"{COMPANY_FILE} not found.")

    with open(COMPANY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["companies"]


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
