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

    filtered_df = monthly.copy()

    if selected_year is not None:
        filtered_df = filtered_df[
            filtered_df["Year"] == selected_year
        ]

    if selected_month is not None:
        filtered_df = filtered_df[
            filtered_df["Month"] == selected_month
        ]

    # ------------------------
    # Company
    # ------------------------
    selected_company = []

    if is_global_user():
        companies = sorted(
            filtered_df["Company"].dropna().unique()
        )

        selected_company = st.sidebar.multiselect(
            "Company",
            companies,
            default=companies,
        )

        if selected_company:
            filtered_df = filtered_df[
                filtered_df["Company"].isin(selected_company)
            ]

    # ------------------------
    # Department
    # ------------------------
    departments = sorted(
        filtered_df["Department"].dropna().unique()
    )

    selected_department = st.sidebar.multiselect(
        "Department",
        departments,
    )

    if selected_department:
        filtered_df = filtered_df[
            filtered_df["Department"].isin(selected_department)
        ]

    # ------------------------
    # Designation
    # ------------------------
    designations = sorted(
        filtered_df["Designation"].dropna().unique()
    )

    selected_designation = st.sidebar.multiselect(
        "Designation",
        designations,
    )

    employee_count = filtered_df["EmpCode"].nunique()
    department_count = filtered_df["Department"].nunique()
    designation_count = filtered_df["Designation"].nunique()

    st.sidebar.markdown("---")

    st.sidebar.info(
        f"""
    **Employees:** {employee_count}

    **Departments:** {department_count}

    **Designations:** {designation_count}
    """
    )

    return (
        selected_year,
        selected_month,
        selected_company,
        selected_department,
        selected_designation,
    )
