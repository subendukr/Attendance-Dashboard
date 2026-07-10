"""
Employee Charts

Reusable employee-level visualizations for the
Neelkamal Attendance Dashboard.
"""

from utils.charts.common import px, COLORS, style_chart, empty_chart


# ==========================================================
# EMPLOYEE ATTENDANCE
# ==========================================================


def employee_attendance_chart(df):
    """
    Present days by employee.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Name", as_index=False)
        .agg(Present=("Present", "sum"))
        .sort_values("Present", ascending=False)
        .head(20)
    )

    fig = px.bar(
        summary,
        x="Name",
        y="Present",
        text="Present",
        color_discrete_sequence=[COLORS["Present"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Top Employees by Present Days")


# ==========================================================
# EMPLOYEE ABSENT DAYS
# ==========================================================


def employee_absent_chart(df):
    """
    Top employees by absent days.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Name", as_index=False)
        .agg(Absent=("Absent", "sum"))
        .sort_values("Absent", ascending=False)
        .head(20)
    )

    fig = px.bar(
        summary,
        x="Name",
        y="Absent",
        text="Absent",
        color_discrete_sequence=[COLORS["Absent"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Top Employees by Absent Days")


# ==========================================================
# EMPLOYEE LEAVE
# ==========================================================


def employee_leave_chart(df):
    """
    Top employees by leave days.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Name", as_index=False)
        .agg(Leave=("Leave", "sum"))
        .sort_values("Leave", ascending=False)
        .head(20)
    )

    fig = px.bar(
        summary,
        x="Name",
        y="Leave",
        text="Leave",
        color_discrete_sequence=[COLORS["Leave"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Top Employees by Leave")


# ==========================================================
# EMPLOYEE PAID DAYS
# ==========================================================


def employee_paiddays_chart(df):
    """
    Paid days by employee.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Name", as_index=False)
        .agg(PaidDays=("PaidDays", "sum"))
        .sort_values("PaidDays", ascending=False)
        .head(20)
    )

    fig = px.bar(
        summary,
        x="Name",
        y="PaidDays",
        text="PaidDays",
        color_discrete_sequence=[COLORS["PaidDays"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Top Employees by Paid Days")


# ==========================================================
# EMPLOYEE WORK HOURS
# ==========================================================


def employee_workhours_chart(df):
    """
    Total work hours by employee.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Name", as_index=False)
        .agg(WorkHours=("WorkHrs", "sum"))
        .sort_values("WorkHours", ascending=False)
        .head(20)
    )

    fig = px.bar(
        summary,
        x="Name",
        y="WorkHours",
        text="WorkHours",
        color_discrete_sequence=[COLORS["WorkHours"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Top Employees by Work Hours")


# ==========================================================
# EMPLOYEE STATUS DISTRIBUTION
# ==========================================================


def employee_status_pie(df):
    """
    Attendance status distribution for EmployeeDaily data.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Status", as_index=False).size().rename(columns={"size": "Count"})
    )

    fig = px.pie(summary, names="Status", values="Count")

    fig.update_traces(textinfo="percent+label")

    return style_chart(fig, title="Attendance Status Distribution", showlegend=True)


# ==========================================================
# EMPLOYEE RANKING
# ==========================================================


def employee_ranking_chart(df):
    """
    Employee attendance ranking.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Name", as_index=False).agg(
        Present=("Present", "sum"), Absent=("Absent", "sum"), Leave=("Leave", "sum")
    )

    summary["AttendancePct"] = (
        summary["Present"]
        / (summary["Present"] + summary["Absent"] + summary["Leave"])
        * 100
    ).round(2)

    summary = summary.sort_values("AttendancePct", ascending=True).tail(20)

    fig = px.bar(
        summary,
        x="AttendancePct",
        y="Name",
        orientation="h",
        text="AttendancePct",
        color_discrete_sequence=[COLORS["Present"]],
    )

    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")

    fig.update_xaxes(range=[0, 100])

    return style_chart(fig, title="Employee Attendance Ranking")


# ==========================================================
# EMPLOYEE ATTENDANCE HISTORY
# ==========================================================


def employee_history_chart(df):
    """
    Daily attendance history for the selected employee.

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered EmployeeDaily dataset for one employee.

    Returns
    -------
    plotly.graph_objects.Figure
    """

    if df.empty:
        return empty_chart("No attendance records available.")

    history = df.copy()

    history = history.sort_values("Date")

    fig = px.scatter(
        history,
        x="Date",
        y="Status",
        color="Status",
        hover_data=["InTime", "OutTime", "WorkHrs", "OTHrs", "Shift"],
        title="Employee Attendance History",
        color_discrete_map={
            "P": COLORS["Present"],
            "P-LT": "#22C55E",
            "A": COLORS["Absent"],
            "L": COLORS["Leave"],
            "H": COLORS["Holiday"],
            "HL": COLORS["Holiday"],
            "WO": "#6B7280",
            "OD": "#0EA5E9",
            "WFH": "#8B5CF6",
        },
    )

    fig.update_traces(marker=dict(size=11, line=dict(width=1, color="white")))

    fig.update_layout(xaxis_title="Date", yaxis_title="Attendance Status")

    return style_chart(fig, title="Employee Attendance History", showlegend=True)


# ==========================================================
# EMPLOYEE OT HISTORY
# ==========================================================


def employee_ot_chart(df):
    """
    Employee overtime chart.
    """

    return empty_chart("Employee Overtime (Coming Soon)")


# ==========================================================
# EMPLOYEE LEAVE HISTORY
# ==========================================================


def employee_leave_history(df):
    """
    Employee leave history.
    """

    return empty_chart("Employee Leave History (Coming Soon)")
