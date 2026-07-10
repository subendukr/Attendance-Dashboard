"""
Company Detection

Determines the company based on the uploaded
attendance workbook filename.
"""

from config.company_config import load_companies


# ==========================================================
# DETECT COMPANY
# ==========================================================


def detect_company(filename):

    filename = filename.upper()

    companies = load_companies()

    for code, details in companies.items():
        if code in filename:
            return details

    return None


def company_from_filename(filename):

    company = detect_company(filename)

    if company is None:
        return "Unknown"

    return company["name"]
