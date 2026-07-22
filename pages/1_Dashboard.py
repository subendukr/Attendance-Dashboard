import streamlit as st
from auth.layout import render_header
from utils.filters import filter_monthly
from utils.metrics import dashboard_metrics
from auth.permissions import require_login
from services.attendance_service import attendance_service
from utils.ui_filters import render_sidebar_filters
from utils.ui_messages import show_no_data_message

from utils.charts.attendance import (
    attendance_summary_chart,
)

from utils.charts.department import (
    department_chart,
    department_employee_chart,
)

from utils.company_ui import show_company_column

from utils.export import (
    dataframe_to_csv,
    dataframe_to_excel,
)

# ==========================================================
# LOAD DATA
# ==========================================================

require_login()

render_header(title="Neelkamal Steel Industry", subtitle="Employee Attendance Dashboard")

monthly = attendance_service.get_monthly_data()

if not attendance_service.has_processed_data():
    show_no_data_message()

monthly = attendance_service.get_monthly_data()

(
    selected_year,
    selected_month,
    selected_company,
    selected_department,
    selected_designation,
) = render_sidebar_filters(monthly, title="📂 Dashboard Filters")

# ==========================================================
# APPLY FILTERS
# ==========================================================

filtered = filter_monthly(
    monthly,
    year=selected_year,
    month=selected_month,
    company=selected_company,
    department=selected_department,
    designation=selected_designation,
)


# ==========================================================
# EMPTY DATA CHECK
# ==========================================================

if filtered.empty:
    st.warning("No attendance records found for the selected filters.")

    st.stop()


# ==========================================================
# DASHBOARD METRICS
# ==========================================================

metrics = dashboard_metrics(filtered)


# ==========================================================
# KPI CARDS
# ==========================================================

st.markdown("## 📈 Attendance Summary")

c1, c2, c3, c4 = st.columns(4)

c5, c6, c7, c8 = st.columns(4)

c1.metric("Employees", metrics["employees"])

c2.metric("Present", metrics["present"])

c3.metric("Absent", metrics["absent"])

c4.metric("Leave", metrics["leave"])

c5.metric("Holiday", metrics["holiday"])

c6.metric("Weekly Off", metrics["weekly_off"])

c7.metric("Paid Days", metrics["paid_days"])

c8.metric("Attendance", f"{metrics['attendance_pct']:.2f}%")


# ==========================================================
# CHARTS
# ==========================================================

st.markdown("## 📊 Dashboard Analytics")

left, right = st.columns(2)

with left:
    st.plotly_chart(attendance_summary_chart(filtered), width="stretch")

with right:
    st.plotly_chart(department_chart(filtered), width="stretch")


st.markdown("## 👥 Department Overview")

st.plotly_chart(department_employee_chart(filtered), width="stretch")

st.divider()

# ==========================================================
# ANALYTICS REGISTER
# ==========================================================

st.markdown("## 📋 Analytics Register")

st.caption("Search, review and export the filtered monthly attendance records.")

search = st.text_input("🔍 Search Employee", placeholder="Employee Code, Name, Department or Designation...",)

register = filtered.copy()

# ==========================================================
# SEARCH FILTER
# ==========================================================

if search:
    searchable = register[["EmpCode", "Name", "Department", "Designation"]].astype(str)

    mask = (
        searchable["EmpCode"].str.contains(search, case=False, na=False)
        | searchable["Name"].str.contains(search, case=False, na=False)
        | searchable["Department"].str.contains(search, case=False, na=False)
        | searchable["Designation"].str.contains(search, case=False, na=False)
    )

    register = register.loc[mask]

# ==========================================================
# REGISTER TABLE
# ==========================================================

display_columns = []

if show_company_column():
    display_columns.append("Company")

display_columns.extend(
    [
        "EmpCode",
        "Name",
        "Department",
        "Designation",
        "Present",
        "Absent",
        "Leave",
        "PaidDays",
        "WorkHrs",
        "OvTim",
    ]
)

st.caption(
    f"""
Displaying {len(register):,} monthly records

Employees : {register["EmpCode"].nunique()}

Departments : {register["Department"].nunique()}
"""
)

st.dataframe(register[display_columns], width="stretch", hide_index=True, height=450)

st.divider()

# ==========================================================
# EXPORT REPORTS
# ==========================================================

st.markdown("## 📥 Export Reports")

st.caption("Download the filtered analytics register.")

csv_data = dataframe_to_csv(register)

excel_data = dataframe_to_excel(register)

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        "⬇ Download CSV",
        csv_data,
        file_name=f"Dashboard_{selected_month}_{selected_year}.csv",
        mime="text/csv",
        width="stretch",
    )

with col2:
    st.download_button(
        "📥 Download Excel",
        excel_data,
        file_name=f"Dashboard_{selected_month}_{selected_year}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )

st.divider()

st.markdown("---")

st.caption(
    f"""
Dashboard Version : 2.0

Generated from processed attendance data.

© Neelkamal Steel Industry
"""
)

from utils.footer import render_footer

# At the end of each page
render_footer()