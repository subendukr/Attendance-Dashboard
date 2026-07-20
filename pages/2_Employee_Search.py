import streamlit as st
import pandas as pd

from utils.data_access import load_daily_data
from utils.filters import filter_daily
from utils.metrics import employee_metrics
from utils.metrics import time_metrics

from utils.export import (dataframe_to_csv, dataframe_to_excel)

from utils.company_ui import is_global_user, show_company_column

from config.company_config import company_details

from auth.layout import render_header
from auth.permissions import require_login

from utils.employee import (
    employee_profile,
    employee_available_years,
    employee_available_months,
    employee_calendar,
    employee_history,
    employee_daily_log,
)

from utils.charts.employee import employee_history_chart, employee_status_pie

from services.attendance_service import attendance_service

def status_style(value):

    colors = {
        "P": "#53d572",
        "A": "#ea2c3c",
        "L": "#d7b133",
        "H": "#28c4e0",
        "WO": "#4486e9",
        "WFH": "#43e369",
        "P-LT": "#88af39",
        "P/2": "#30d5bc",
    }

    color = colors.get(str(value), "")

    return f"background-color: {color}; font-weight: bold;"


# ==========================================================
# LOAD DATA
# ==========================================================
require_login()

render_header(title="Neelkamal Steel Industry", subtitle="Employee Search")

daily = load_daily_data()
# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("🔍 Employee Filters")

st.sidebar.markdown("---")

# ==========================================================
# COMPANY FILTER (ADMIN ONLY)
# ==========================================================

selected_companies = None

if is_global_user():
    companies = sorted(daily["Company"].dropna().unique())

    selected_companies = st.sidebar.multiselect("Company", companies, default=companies)

if selected_companies:
    daily = daily[daily["Company"].isin(selected_companies)]


# ==========================================================
# EMPLOYEE SELECTOR
# ==========================================================

employees = (
    daily[["EmpCode", "Name"]]
    .drop_duplicates()
    .sort_values("Name")
    .reset_index(drop=True)
)

if daily.empty:
    st.warning("No employees found for the selected company.")

    st.stop()

# Ensure consistent string type

employees["EmpCode"] = employees["EmpCode"].astype(str)

employees["Name"] = employees["Name"].astype(str)

employees["Display"] = employees["Name"] + " (" + employees["EmpCode"] + ")"

selected = st.sidebar.selectbox("Select Employee", employees["Display"])

selected_empcode = selected.split("(")[1].replace(")", "")
# ==========================================================
# AVAILABLE YEARS
# ==========================================================

years = employee_available_years(daily, selected_empcode)

selected_year = st.sidebar.selectbox("Year", years)


# ==========================================================
# AVAILABLE MONTHS
# ==========================================================

months = employee_available_months(daily, selected_empcode, selected_year)

selected_month = st.sidebar.selectbox("Month", months)

# ==========================================================
# SIDEBAR SUMMARY
# ==========================================================

st.sidebar.markdown("---")

st.sidebar.info(
    f"""

Employee Code : {selected_empcode}

Available Years : {len(years)}

Available Months : {len(months)}

Selected Period : {selected_month} {selected_year}

"""
)


# ==========================================================
# APPLY FILTERS
# ==========================================================

employee_df = filter_daily(daily, empcode=selected_empcode, year=selected_year, month=selected_month)

employee_df = employee_df.sort_values("Date")

# ==========================================================
# EMPTY DATA CHECK
# ==========================================================

if employee_df.empty:
    st.warning("No attendance records found.")
    st.stop()


# ==========================================================
# EMPLOYEE PROFILE
# ==========================================================

profile = employee_profile(employee_df, selected_empcode)

st.markdown("## 👤 Employee Information")

left, right = st.columns(2)

with left:
    if "Name" in profile:
        st.write("**Name:**", profile["Name"])

    if show_company_column():
        company = company_details(profile["Company"])

        st.write("**Company:**", company["name"] if company else profile["Company"])

    if "Department" in profile:
        st.write("**Department:**", profile["Department"])

with right:
    if "Designation" in profile:
        st.write("**Designation:**", profile["Designation"])

    st.write("**Shift:**", profile["Shift"])

st.markdown("---")

st.caption(f"Viewing attendance for {selected_month} {selected_year}")

# ==========================================================
# EMPLOYEE METRICS
# ==========================================================

attendance = employee_metrics(employee_df)

time = time_metrics(employee_df)


# ==========================================================
# ATTENDANCE KPI CARDS
# ==========================================================

st.markdown("## 📈 Attendance Summary")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Present", attendance["present"])

c2.metric("Absent", attendance["absent"])

c3.metric("Leave", attendance["leave"])

c4.metric("Holiday", attendance["holiday"])

c5.metric("Attendance", f"{attendance['attendance_pct']:.2f}%")


# ==========================================================
# TIME KPI CARDS
# ==========================================================

st.markdown("## ⏰ Attendance Time Summary")

t1, t2, t3, t4 = st.columns(4)

t1.metric("Average In", time["avg_in"])

t2.metric("Average Out", time["avg_out"])

t3.metric("Average Work", time["avg_work"])

t4.metric("Total OT", time["ot"])


# ==========================================================
# ATTENDANCE ANALYTICS
# ==========================================================

st.markdown("## 📊 Attendance Analytics")

left, right = st.columns(2)

with left:
    st.plotly_chart(employee_history_chart(employee_df), width="stretch")

with right:
    st.plotly_chart(employee_status_pie(employee_df), width="stretch")


# ==========================================================
# MONTHLY HISTORY
# ==========================================================

st.markdown(f"## 📈 Monthly Attendance History ({selected_month} {selected_year})")

history = employee_history(employee_df, selected_empcode)

st.dataframe(history, width="stretch", hide_index=True)


# ==========================================================
# ATTENDANCE CALENDAR
# ==========================================================

st.markdown(f"## 🗓 Attendance Calendar ({selected_month} {selected_year})")

calendar = employee_calendar(employee_df)

styled_calendar = calendar.style.map(status_style)

st.dataframe(styled_calendar, width="stretch", hide_index=True)


# ==========================================================
# DAILY ATTENDANCE LOG
# ==========================================================

st.markdown(f"## 📋 Daily Attendance Log ({selected_month} {selected_year})")

daily_log = employee_daily_log(employee_df)

# Format Date column (remove time component)
if "Date" in daily_log.columns:
    daily_log["Date"] = (
        pd.to_datetime(daily_log["Date"])
        .dt.strftime("%Y-%m-%d")
    )

# ----------------------------------------------------------
# FILTERS
# ----------------------------------------------------------

filter_col, search_col = st.columns(2)

with filter_col:
    status_filter = st.selectbox("Status Filter", ["All", "P", "A", "L", "H", "WO", "WFH"])

with search_col:
    search = st.text_input(
        "🔍 Search Daily Attendance",
        placeholder="Search by Date, Shift, In Time or Out Time...",
    )

if status_filter != "All":
    daily_log = daily_log[daily_log["Status"] == status_filter]

# ----------------------------------------------------------
# SEARCH
# ----------------------------------------------------------

if search:
    searchable = daily_log[["Date", "Shift", "InTime", "OutTime"]].astype(str)

    mask = searchable.apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)

    daily_log = daily_log.loc[mask]

st.caption(f"{len(daily_log)} record(s) found.")

styled_log = daily_log.style.map(status_style, subset=["Status"])

st.dataframe(styled_log, width="stretch", hide_index=True, height=450)
# ==========================================================
# EXPORT REPORTS
# ==========================================================

st.markdown("---")

with st.container(border=True):
    st.subheader("📥 Export Reports")

    csv = dataframe_to_csv(daily_log)

    excel_data = dataframe_to_excel(daily_log)

    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "⬇ Download CSV", csv, file_name=f"{selected_empcode}_{selected_month}_{selected_year}.csv", mime="text/csv", width="stretch",
        )

    with c2:
        st.download_button(
            "📥 Download Excel",
            excel_data,
            file_name=f"{selected_empcode}_{selected_month}_{selected_year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

    st.caption(f"Exporting {len(daily_log)} attendance record(s).")

# ==========================================================
# DATA SUMMARY
# ==========================================================

st.markdown("---")

summary1, summary2, summary3 = st.columns(3)

summary1.metric("Attendance Records", len(employee_df))

summary2.metric("Present Days", attendance["present"])

summary3.metric("Current Shift", profile["Shift"])


# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")

st.caption(
    f"""

Employee Search Version : v1.0

Employee : {profile.get("Name", "")}

Employee Code : {selected_empcode}

Department : {profile.get("Department", "")}

Designation : {profile.get("Designation", "")}

Showing : {selected_month} {selected_year}

"""
)

if show_company_column():
    company = company_details(profile["Company"])

    st.caption(f"Company : {company['name'] if company else profile['Company']}")


# ==========================================================
# LAST UPDATED
# ==========================================================

last_updated = attendance_service.get_processed_last_updated()

if last_updated:
    st.caption(f"Processed Data Updated: {last_updated:%d-%b-%Y %H:%M}")
