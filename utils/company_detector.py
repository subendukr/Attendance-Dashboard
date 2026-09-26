import streamlit as st

def detect_company(filename):
    """
    Detect company from uploaded workbook filename.

    Longer company codes are checked first so that
    NLKL OFC is detected as NLKL OFC instead of NLKL.
    """

    filename = str(filename).strip().upper()

    # Import here to avoid circular import:
    # repository.py -> company_detector.py -> repository.py
    from utils.repository import load_companies

    @st.cache_data(ttl=3600)
    def _load_companies_cached():
        return load_companies()

    data = _load_companies_cached()

    # repository.load_companies() returns the complete
    # companies.json structure.
    companies = data.get("companies", {})

    # Check longest/specific company codes first.
    for code, details in sorted(
        companies.items(),
        key=lambda item: len(str(item[0])),
        reverse=True,
    ):
        code = str(code).strip().upper()

        if code in filename:
            return details

    return None


def company_from_filename(filename):
    company = detect_company(filename)

    if company is None:
        return "Unknown"

    return company["name"]