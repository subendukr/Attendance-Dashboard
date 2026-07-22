import streamlit as st
from datetime import datetime
from auth.layout import render_header
from auth.permissions import require_login
from utils.metrics import dashboard_metrics
from utils.ui_filters import render_sidebar_filters
from utils.ui_messages import show_no_data_message
from utils.filters import filter_monthly, filter_daily
from analytics.attendance import monthly_attendance_trend
from services.attendance_service import attendance_service
from utils.charts.department import department_status_chart

from utils.analytics import (
    department_performance,
    designation_performance,
    top_absentees,
    overtime_summary,
)
from utils.charts.attendance import (
    attendance_summary_chart,
    attendance_pie_chart,
    attendance_trend_chart,
    attendance_count_chart,
)
# ==========================================================
# LOAD DATASETS
# ==========================================================
require_login()

render_header(title="Neelkamal Steel Industry", subtitle="Attendance Analytics")

if not attendance_service.has_processed_data():
    show_no_data_message()

monthly = attendance_service.get_monthly_data()
daily = attendance_service.get_daily_data()

(
    selected_year,
    selected_month,
    selected_company,
    selected_departments,
    selected_designations,
) = render_sidebar_filters(monthly, title="📊 Analytics Filters")



# ==========================================================
# TREND DATASET
# (Month Filter Not Applied)
# ==========================================================

trend_df = filter_monthly(
    monthly,
    year=selected_year,
    month=None,
    company=selected_company,
    department=selected_departments,
    designation=selected_designations,
)


# ==========================================================
# FILTERED MONTHLY DATA
# ==========================================================

monthly_filtered = filter_monthly(
    monthly,
    year=selected_year,
    month=selected_month,
    company=selected_company,
    department=selected_departments,
    designation=selected_designations,
)


# ==========================================================
# FILTERED DAILY DATA
# ==========================================================

daily_filtered = filter_daily(
    daily,
    year=selected_year,
    month=selected_month,
    company=selected_company,
    department=selected_departments,
    designation=selected_designations,
)


# ==========================================================
# ATTENDANCE SUMMARY
# ==========================================================

attendance_summary = monthly_attendance_trend(trend_df)


# ==========================================================
# EMPTY DATA CHECK
# ==========================================================

if monthly_filtered.empty:
    st.warning("No attendance records found for the selected filters.")

    st.stop()


# ==========================================================
# PREPARE ANALYTICS DATA
# ==========================================================

dashboard = dashboard_metrics(monthly_filtered)

department_data = department_performance(monthly_filtered)

designation_data = designation_performance(monthly_filtered)

top_absent = top_absentees(monthly_filtered, n=10)

overtime_data = overtime_summary(daily_filtered)


# ==========================================================
# ANALYTICS SUMMARY
# ==========================================================

st.markdown("## 📊 Analytics Summary")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Employees", dashboard["employees"])

k2.metric("Present", dashboard["present"])

k3.metric("Absent", dashboard["absent"])

k4.metric("Leave", dashboard["leave"])

k5.metric("Paid Days", round(dashboard["paid_days"], 2))

k6.metric("Attendance", f"{dashboard['attendance_pct']:.2f}%")

st.divider()

# ==========================================================
# ATTENDANCE ANALYTICS
# ==========================================================

st.markdown("## 📈 Attendance Analytics")

st.caption("Monthly attendance performance, distribution and trend analysis.")

# ==========================================================
# ATTENDANCE SUMMARY CHARTS
# ==========================================================

left, right = st.columns(2)

with left:
    st.plotly_chart(attendance_summary_chart(monthly_filtered), width="stretch")

with right:
    st.plotly_chart(attendance_pie_chart(monthly_filtered), width="stretch")

# ==========================================================
# MONTHLY ATTENDANCE TREND
# ==========================================================

st.subheader("Monthly Attendance Trend")

st.plotly_chart(attendance_trend_chart(attendance_summary), width="stretch")

# ==========================================================
# MONTHLY STATUS COMPARISON
# ==========================================================

st.subheader("Present vs Absent vs Leave")

st.plotly_chart(attendance_count_chart(attendance_summary), width="stretch")

# ==========================================================
# MONTHLY ATTENDANCE TABLE
# ==========================================================

st.subheader("Attendance Summary")

st.dataframe(attendance_summary, width="stretch", hide_index=True)

# ==========================================================
# ATTENDANCE INSIGHTS
# ==========================================================

st.subheader("💡 Attendance Insights")

if len(attendance_summary) > 1:
    best_month = attendance_summary.loc[attendance_summary["AttendancePct"].idxmax()]

    worst_month = attendance_summary.loc[attendance_summary["AttendancePct"].idxmin()]

    c1, c2 = st.columns(2)

    with c1:
        st.success(
            f"""
🏆 Highest Attendance

Month : {best_month["Month"]}

Attendance : {best_month["AttendancePct"]:.2f}%
"""
        )

    with c2:
        st.warning(
            f"""
⚠ Lowest Attendance

Month : {worst_month["Month"]}

Attendance : {worst_month["AttendancePct"]:.2f}%
"""
        )

else:
    month = attendance_summary.iloc[0]

    st.info(
        f"""
Attendance for **{month["Month"]}**

Attendance : **{month["AttendancePct"]:.2f}%**
"""
    )

st.divider()

# ==========================================================
# PRESENT VS ABSENT VS LEAVE
# ==========================================================

st.subheader("Present vs Absent vs Leave")

st.plotly_chart(department_status_chart(monthly_filtered), width="stretch")

# ==========================================================
# DEPARTMENT PERFORMANCE TABLE
# ==========================================================

st.subheader("Department Performance Table")

st.dataframe(department_data, width="stretch", hide_index=True)

# ==========================================================
# DEPARTMENT INSIGHTS
# ==========================================================

st.subheader("💡 Department Insights")

best_department = department_data.loc[department_data["Attendance %"].idxmax()]

worst_department = department_data.loc[department_data["Attendance %"].idxmin()]

largest_department = department_data.loc[department_data["Employees"].idxmax()]

smallest_department = department_data.loc[department_data["Employees"].idxmin()]

r1c1, r1c2 = st.columns(2)

with r1c1:
    st.success(
        f"""
🏆 Best Department

Department : {best_department["Department"]}

Attendance : {best_department["Attendance %"]:.2f}%
"""
    )

with r1c2:
    st.warning(
        f"""
⚠ Lowest Attendance

Department : {worst_department["Department"]}

Attendance : {worst_department["Attendance %"]:.2f}%
"""
    )

r2c1, r2c2 = st.columns(2)

with r2c1:
    st.info(
        f"""
👥 Largest Department

Department : {largest_department["Department"]}

Employees : {largest_department["Employees"]}
"""
    )

with r2c2:
    st.info(
        f"""
🏢 Smallest Department

Department : {smallest_department["Department"]}

Employees : {smallest_department["Employees"]}
"""
    )

st.divider()

# ==========================================================
# DESIGNATION ANALYTICS
# ==========================================================

st.markdown("## 👷 Designation Analytics")

st.caption("Designation-wise workforce summary.")

st.dataframe(designation_data, width="stretch", hide_index=True)

st.divider()

# ==========================================================
# EMPLOYEE INSIGHTS
# ==========================================================

st.markdown("## 👤 Employee Insights")

left, right = st.columns(2)

with left:
    st.subheader("Top Absentees")

    st.dataframe(top_absent, width="stretch", hide_index=True)

with right:
    st.subheader("Overtime Summary")

    st.dataframe(overtime_data, width="stretch", hide_index=True)

st.divider()

# ==========================================================
# DATA INFORMATION
# ==========================================================

st.markdown("## ℹ Dataset Information")

updated = attendance_service.get_processed_last_updated()

if updated:

    info1, info2 = st.columns(2)

    with info1:
        st.info(
            f"""
Processed Dataset

Updated

{updated:%d-%b-%Y %H:%M}
"""
        )

    with info2:
        st.info(
            f"""
Current Filters

Year : {selected_year}

Month : {selected_month}
"""
        )

# ==========================================================
# PAGE SUMMARY
# ==========================================================

st.markdown("## 📌 Dashboard Summary")

summary1, summary2 = st.columns(2)

summary1.metric("Employees", monthly_filtered["EmpCode"].nunique())

summary2.metric("Departments", monthly_filtered["Department"].nunique())
st.divider()

# ==========================================================
# FOOTER
# ==========================================================

left, right = st.columns(2)

with left:
    st.caption("""Dashboard Version 2.0""")

    st.caption("© Neelkamal Steel Industry")

with right:
    st.caption(
        f"""
Generated

{datetime.now():%d-%b-%Y %H:%M}

"""
    )

from utils.footer import render_footer

# At the end of each page
render_footer()