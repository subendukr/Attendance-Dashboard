"""
Department Charts

Reusable department-level visualizations for the
Neelkamal Attendance Dashboard.
"""

from utils.charts.common import px, COLORS, style_chart, empty_chart

# ==========================================================
# DEPARTMENT ATTENDANCE
# ==========================================================


def department_chart(df):
    """
    Attendance percentage by Department.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Department", as_index=False).agg(
        Present=("Present", "sum"), Absent=("Absent", "sum"), Leave=("Leave", "sum")
    )

    summary["AttendancePct"] = (
        summary["Present"]
        / (summary["Present"] + summary["Absent"] + summary["Leave"])
        * 100
    ).round(2)

    summary = summary.sort_values("AttendancePct", ascending=False)

    fig = px.bar(
        summary,
        x="Department",
        y="AttendancePct",
        text="AttendancePct",
        color="AttendancePct",
        color_continuous_scale="Greens",
    )

    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")

    fig.update_yaxes(range=[0, 100], title="Attendance %")

    return style_chart(fig, title="Department Attendance Percentage")


# ==========================================================
# DEPARTMENT ATTENDANCE %
# ==========================================================


def department_attendance_percentage(df):
    """
    Attendance percentage by Department.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Department", as_index=False).agg(
        Present=("Present", "sum"), Absent=("Absent", "sum"), Leave=("Leave", "sum")
    )

    summary["AttendancePct"] = (
        summary["Present"]
        / (summary["Present"] + summary["Absent"] + summary["Leave"])
        * 100
    ).round(2)

    summary = summary.sort_values("AttendancePct", ascending=False)

    fig = px.bar(
        summary,
        x="Department",
        y="AttendancePct",
        text="AttendancePct",
        color_discrete_sequence=[COLORS["Present"]],
    )

    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")

    fig.update_yaxes(range=[0, 100], title="Attendance %")

    return style_chart(fig, title="Department Attendance Percentage")


# ==========================================================
# DEPARTMENT EMPLOYEE COUNT
# ==========================================================


def department_employee_chart(df):
    """
    Employee count by Department.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Department", as_index=False)
        .agg(Employees=("EmpCode", "nunique"))
        .sort_values("Employees", ascending=False)
    )

    fig = px.bar(
        summary,
        x="Department",
        y="Employees",
        text="Employees",
        color_discrete_sequence=[COLORS["Department"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Employees by Department")


# ==========================================================
# DEPARTMENT STATUS COMPARISON
# ==========================================================


def department_status_chart(df):
    """
    Compare Present, Absent and Leave
    across departments.
    """

    if df.empty:
        return empty_chart("No department data available.")

    summary = df.groupby("Department", as_index=False)[
        ["Present", "Absent", "Leave"]
    ].sum()

    chart_data = summary.melt(
        id_vars="Department",
        value_vars=["Present", "Absent", "Leave"],
        var_name="Status",
        value_name="Days",
    )

    fig = px.bar(
        chart_data,
        x="Department",
        y="Days",
        color="Status",
        barmode="group",
        color_discrete_map={
            "Present": COLORS["Present"],
            "Absent": COLORS["Absent"],
            "Leave": COLORS["Leave"],
        },
        title="Present vs Absent vs Leave by Department",
    )

    fig.update_layout(xaxis_title="Department", yaxis_title="Days")

    return style_chart(
        fig, title="Present vs Absent vs Leave by Department", showlegend=True
    )


# ==========================================================
# DEPARTMENT ABSENT DAYS
# ==========================================================


def department_absent_chart(df):
    """
    Total Absent Days by Department.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Department", as_index=False)
        .agg(Absent=("Absent", "sum"))
        .sort_values("Absent", ascending=False)
    )

    fig = px.bar(
        summary,
        x="Department",
        y="Absent",
        text="Absent",
        color_discrete_sequence=[COLORS["Absent"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Department Absenteeism")


# ==========================================================
# DEPARTMENT LEAVE DAYS
# ==========================================================


def department_leave_chart(df):
    """
    Total Leave Days by Department.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Department", as_index=False)
        .agg(Leave=("Leave", "sum"))
        .sort_values("Leave", ascending=False)
    )

    fig = px.bar(
        summary,
        x="Department",
        y="Leave",
        text="Leave",
        color_discrete_sequence=[COLORS["Leave"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Department Leave")


# ==========================================================
# DEPARTMENT PAID DAYS
# ==========================================================


def department_paiddays_chart(df):
    """
    Paid Days by Department.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Department", as_index=False)
        .agg(PaidDays=("PaidDays", "sum"))
        .sort_values("PaidDays", ascending=False)
    )

    fig = px.bar(
        summary,
        x="Department",
        y="PaidDays",
        text="PaidDays",
        color_discrete_sequence=[COLORS["PaidDays"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Department Paid Days")


# ==========================================================
# DEPARTMENT WORK HOURS
# ==========================================================


def department_workhours_chart(df):
    """
    Total Work Hours by Department.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Department", as_index=False)
        .agg(WorkHours=("WorkHrs", "sum"))
        .sort_values("WorkHours", ascending=False)
    )

    fig = px.bar(
        summary,
        x="Department",
        y="WorkHours",
        text="WorkHours",
        color_discrete_sequence=[COLORS["WorkHours"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Department Work Hours")


# ==========================================================
# DEPARTMENT RANKING
# ==========================================================


def department_ranking_chart(df):
    """
    Rank departments by attendance percentage.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Department", as_index=False).agg(
        Present=("Present", "sum"), Absent=("Absent", "sum"), Leave=("Leave", "sum")
    )

    summary["AttendancePct"] = (
        summary["Present"]
        / (summary["Present"] + summary["Absent"] + summary["Leave"])
        * 100
    ).round(2)

    summary = summary.sort_values("AttendancePct", ascending=True)

    fig = px.bar(
        summary,
        x="AttendancePct",
        y="Department",
        orientation="h",
        text="AttendancePct",
        color_discrete_sequence=[COLORS["Present"]],
    )

    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")

    fig.update_xaxes(range=[0, 100])

    return style_chart(fig, title="Department Attendance Ranking")
