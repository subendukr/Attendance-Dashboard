import streamlit as st
from auth.layout import render_header
from utils.filters import filter_monthly
from utils.metrics import dashboard_metrics
from auth.permissions import require_login
from services.attendance_service import attendance_service
from utils.ui_filters import render_sidebar_filters

from utils.charts.attendance import (
    attendance_summary_chart,
)

from utils.charts.department import (
    department_chart,
    department_employee_chart,
)

# ==========================================================
# LOAD DATA
# ==========================================================

require_login()

render_header(
    title="Neelkamal Steel Industry", subtitle="Employee Attendance Dashboard"
)

monthly = attendance_service.get_monthly_data()

if not attendance_service.has_processed_data():

    st.info(
        """
## 📂 Attendance data is currently unavailable.

Please contact the HR Department to upload the Monthly and Daily Attendance records.
Thank you

### Contact:
📞 7488773716
📧 subendu.neelkamal110@gmail.com
"""
    )

    st.stop()

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


st.markdown("---")

st.caption(
    f"""
Dashboard Version : 2.0

Employees Displayed : {metrics["employees"]}

Departments : {filtered["Department"].nunique()}

Generated from processed attendance data.

© Neelkamal Steel Industry
"""
)
