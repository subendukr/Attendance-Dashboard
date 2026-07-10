import streamlit as st
from utils.company_ui import is_global_user

def render_sidebar_filters(monthly, title="📂 Dashboard Filters"):
    """
    Renders common sidebar filters for attendance datasets
    and returns the selected filter values.
    """
    st.sidebar.title(title)
    st.sidebar.markdown("---")
    st.sidebar.caption("Filter attendance records")

    # ------------------------
    # Year
    # ------------------------
    years = sorted(monthly["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox("Year", years) if len(years) > 0 else None

    # ------------------------
    # Month
    # ------------------------
    month_order = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    
    if selected_year is not None:
        months_in_data = monthly.loc[monthly["Year"] == selected_year, "Month"].dropna().unique()
    else:
        months_in_data = monthly["Month"].dropna().unique()
        
    months = [m for m in month_order if m in months_in_data]
    selected_month = st.sidebar.selectbox("Month", months) if len(months) > 0 else None

    # ------------------------
    # Company
    # ------------------------
    selected_company = []
    if is_global_user():
        companies = sorted(monthly["Company"].dropna().unique())
        selected_company = st.sidebar.multiselect("Company", companies, default=companies)

    # ------------------------
    # Department
    # ------------------------
    departments = sorted(monthly["Department"].dropna().unique())
    selected_department = st.sidebar.multiselect("Department", departments)

    # ------------------------
    # Designation
    # ------------------------
    designations = sorted(monthly["Designation"].dropna().unique())
    selected_designation = st.sidebar.multiselect("Designation", designations)

    st.sidebar.markdown("---")
    st.sidebar.info(
        f"""
**Employees:** {monthly["EmpCode"].nunique()}

**Departments:** {monthly["Department"].nunique()}
"""
    )

    return (
        selected_year,
        selected_month,
        selected_company,
        selected_department,
        selected_designation,
    )
