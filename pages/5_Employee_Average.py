import streamlit as st
import pandas as pd
from io import BytesIO

from services.employee_average_service import get_employee_average_data
from utils.data_access import load_daily_data

# ------------------------------------------------------
# PAGE HEADER
# ------------------------------------------------------

st.title("📊 Employee Average Data")
st.caption(
    "Employee-wise attendance averages based on the uploaded attendance reports."
)


# ------------------------------------------------------
# LOAD DATA FOR FILTER OPTIONS
# ------------------------------------------------------

try:
    daily_df = load_daily_data()
except Exception as exc:
    st.error(f"Unable to load attendance data: {exc}")
    st.stop()


if daily_df is None or daily_df.empty:
    st.info("No attendance data is available.")
    st.stop()


# ------------------------------------------------------
# FILTER OPTIONS
# ------------------------------------------------------

filter_col1, filter_col2, filter_col3 = st.columns(3)


# Year
years = []

if "Date" in daily_df.columns:
    dates = pd.to_datetime(
        daily_df["Date"],
        errors="coerce"
    )

    years = sorted(
        dates.dropna().dt.year.unique().tolist(),
        reverse=True
    )

if not years:
    st.warning("No valid attendance dates are available.")
    st.stop()


with filter_col1:
    selected_year = st.selectbox(
        "Year",
        years,
        index=0,
        key="employee_average_year"
    )


# Month
month_order = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

available_months = []

if "Date" in daily_df.columns:
    filtered_dates = pd.to_datetime(
        daily_df["Date"],
        errors="coerce"
    )

    filtered_dates = filtered_dates[
        filtered_dates.dt.year == int(selected_year)
    ]

    available_month_numbers = sorted(
        filtered_dates.dropna().dt.month.unique().tolist()
    )

    available_months = [
        month_order[number - 1]
        for number in available_month_numbers
    ]

if not available_months:
    st.warning(
        f"No attendance data is available for {selected_year}."
    )
    st.stop()


with filter_col2:
    selected_month = st.selectbox(
        "Month",
        available_months,
        index=len(available_months) - 1,
        key="employee_average_month"
    )


# Department
departments = []

if "Department" in daily_df.columns:
    departments = sorted(
        daily_df["Department"]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
        .tolist()
    )

department_options = ["All Departments"] + departments


with filter_col3:
    selected_department = st.selectbox(
        "Department",
        department_options,
        key="employee_average_department"
    )


department_filter = (
    None
    if selected_department == "All Departments"
    else selected_department
)


# ------------------------------------------------------
# LOAD EMPLOYEE AVERAGE DATA
# ------------------------------------------------------

try:
    df = get_employee_average_data(
        year=selected_year,
        month=selected_month,
        department=department_filter,
    )
except Exception as exc:
    st.error(
        f"Unable to calculate employee average data: {exc}"
    )
    st.stop()


# ------------------------------------------------------
# EMPLOYEE SEARCH
# ------------------------------------------------------

search = st.text_input(
    "🔎 Search Employee",
    placeholder="Search by employee code or name..."
)


if search.strip():
    search_text = search.strip().lower()

    df = df[
        df["EmpCode"]
        .astype(str)
        .str.lower()
        .str.contains(search_text, na=False)
        |
        df["Name"]
        .astype(str)
        .str.lower()
        .str.contains(search_text, na=False)
    ].copy()


# ------------------------------------------------------
# SUMMARY
# ------------------------------------------------------

st.markdown("---")

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.metric(
        "Employees",
        len(df)
    )

with summary_col2:
    st.metric(
        "Total Present",
        f"{df['Total Present'].sum():g}"
        if not df.empty
        else "0"
    )

with summary_col3:
    st.metric(
        "Total Absent",
        f"{df['Absent'].sum():g}"
        if not df.empty
        else "0"
    )


# ------------------------------------------------------
# DATA TABLE
# ------------------------------------------------------

st.markdown("### Employee Attendance Summary")


if df.empty:
    st.info(
        "No employee attendance data found for the selected filters."
    )
    st.stop()


display_df = df.rename(
    columns={
        "EmpCode": "Employee Code",
        "Name": "Employee Name",
        "Department": "Department",
        "Designation": "Designation",
        "Avg In Time": "Avg In Time",
        "Avg Out Time": "Avg Out Time",
        "Avg Working Hours": "Avg Working Hours",
        "Total Present": "Total Present",
        "Absent": "Absent",
    }
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)


# ------------------------------------------------------
# EXCEL EXPORT
# ------------------------------------------------------

excel_buffer = BytesIO()

with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl"
) as writer:
    display_df.to_excel(
        writer,
        index=False,
        sheet_name="Employee Average"
    )

excel_buffer.seek(0)

st.download_button(
    label="📊 Download Excel",
    data=excel_buffer,
    file_name=(
        f"employee_average_"
        f"{selected_year}_{selected_month}.xlsx"
    ),
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
)


# ------------------------------------------------------
# CSV EXPORT
# ------------------------------------------------------

csv_data = display_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download CSV",
    data=csv_data,
    file_name=(
        f"employee_average_"
        f"{selected_year}_{selected_month}.csv"
    ),
    mime="text/csv",
)