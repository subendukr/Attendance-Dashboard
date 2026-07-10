"""
Shift Charts

Reusable shift-based visualizations for the
Neelkamal Attendance Dashboard.
"""

from utils.charts.common import px, COLORS, style_chart, empty_chart


# ==========================================================
# SHIFT DISTRIBUTION
# ==========================================================


def shift_distribution_chart(df):
    """
    Employee distribution by shift.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Shift", as_index=False)
        .agg(Employees=("EmpCode", "nunique"))
        .sort_values("Employees", ascending=False)
    )

    fig = px.bar(
        summary,
        x="Shift",
        y="Employees",
        text="Employees",
        color_discrete_sequence=[COLORS["Department"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Employee Distribution by Shift")


# ==========================================================
# SHIFT ATTENDANCE
# ==========================================================


def shift_attendance_chart(df):
    """
    Present days by shift.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Shift", as_index=False).agg(Present=("Present", "sum"))

    fig = px.bar(
        summary,
        x="Shift",
        y="Present",
        text="Present",
        color_discrete_sequence=[COLORS["Present"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Attendance by Shift")


# ==========================================================
# SHIFT ATTENDANCE %
# ==========================================================


def shift_attendance_percentage(df):
    """
    Attendance percentage by shift.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Shift", as_index=False).agg(
        Present=("Present", "sum"), Absent=("Absent", "sum"), Leave=("Leave", "sum")
    )

    summary["AttendancePct"] = (
        summary["Present"]
        / (summary["Present"] + summary["Absent"] + summary["Leave"])
        * 100
    ).round(2)

    fig = px.bar(
        summary,
        x="Shift",
        y="AttendancePct",
        text="AttendancePct",
        color_discrete_sequence=[COLORS["Present"]],
    )

    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")

    fig.update_yaxes(range=[0, 100])

    return style_chart(fig, title="Shift Attendance Percentage")


# ==========================================================
# SHIFT ABSENT DAYS
# ==========================================================


def shift_absent_chart(df):
    """
    Absent days by shift.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Shift", as_index=False).agg(Absent=("Absent", "sum"))

    fig = px.bar(
        summary,
        x="Shift",
        y="Absent",
        text="Absent",
        color_discrete_sequence=[COLORS["Absent"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Absent Days by Shift")


# ==========================================================
# SHIFT LEAVE
# ==========================================================


def shift_leave_chart(df):
    """
    Leave days by shift.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Shift", as_index=False).agg(Leave=("Leave", "sum"))

    fig = px.bar(
        summary,
        x="Shift",
        y="Leave",
        text="Leave",
        color_discrete_sequence=[COLORS["Leave"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Leave by Shift")


# ==========================================================
# SHIFT WORK HOURS
# ==========================================================


def shift_workhours_chart(df):
    """
    Total work hours by shift.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Shift", as_index=False).agg(WorkHours=("WorkHrs", "sum"))

    fig = px.bar(
        summary,
        x="Shift",
        y="WorkHours",
        text="WorkHours",
        color_discrete_sequence=[COLORS["WorkHours"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Work Hours by Shift")


# ==========================================================
# SHIFT OVERTIME
# ==========================================================


def shift_overtime_chart(df):
    """
    Overtime by shift.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Shift", as_index=False).agg(Overtime=("OvTim", "sum"))

    fig = px.bar(
        summary,
        x="Shift",
        y="Overtime",
        text="Overtime",
        color_discrete_sequence=[COLORS["OT"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Overtime by Shift")


# ==========================================================
# SHIFT SHARE
# ==========================================================


def shift_pie_chart(df):
    """
    Employee share by shift.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Shift", as_index=False).agg(Employees=("EmpCode", "nunique"))

    fig = px.pie(summary, names="Shift", values="Employees")

    fig.update_traces(textinfo="percent+label")

    return style_chart(fig, title="Shift Distribution", showlegend=True)


# ==========================================================
# SHIFT COMPARISON
# ==========================================================


def shift_comparison_chart(df):
    """
    Compare Present, Absent and Leave by shift.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Shift", as_index=False).agg(
        Present=("Present", "sum"), Absent=("Absent", "sum"), Leave=("Leave", "sum")
    )

    melted = summary.melt(
        id_vars="Shift",
        value_vars=["Present", "Absent", "Leave"],
        var_name="Status",
        value_name="Days",
    )

    fig = px.bar(
        melted,
        x="Shift",
        y="Days",
        color="Status",
        color_discrete_map=COLORS,
        barmode="group",
    )

    return style_chart(fig, title="Shift Attendance Comparison")


# ==========================================================
# SHIFT HEATMAP
# ==========================================================


def shift_heatmap(df):
    """
    Reserved for future implementation.
    """

    return empty_chart("Shift Heatmap (Coming Soon)")
