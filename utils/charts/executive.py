"""
Executive Dashboard Charts

High-level visualizations for the
Neelkamal Attendance Dashboard.
"""

from utils.charts.common import (
    pd,
    px,
    go,
    COLORS,
    style_chart,
    sort_months,
    empty_chart,
)


# ==========================================================
# COMPANY ATTENDANCE KPI
# ==========================================================


def company_attendance_gauge(attendance_pct):
    """
    Overall company attendance gauge.
    """

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(attendance_pct),
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": COLORS["Present"]},
                "steps": [
                    {"range": [0, 70], "color": "#FECACA"},
                    {"range": [70, 90], "color": "#FDE68A"},
                    {"range": [90, 100], "color": "#BBF7D0"},
                ],
            },
        )
    )

    return style_chart(fig, title="Overall Attendance")


# ==========================================================
# COMPANY ATTENDANCE TREND
# ==========================================================


def executive_attendance_trend(summary):
    """
    Company attendance percentage trend.
    """

    if summary.empty:
        return empty_chart()

    summary = sort_months(summary)

    fig = px.line(summary, x="Month", y="AttendancePct", markers=True)

    fig.update_traces(line=dict(width=4, color=COLORS["Present"]))

    fig.update_yaxes(range=[0, 100])

    return style_chart(fig, title="Company Attendance Trend")


# ==========================================================
# COMPANY ATTENDANCE BREAKDOWN
# ==========================================================


def executive_attendance_breakdown(df):
    """
    Present / Absent / Leave distribution.
    """

    if df.empty:
        return empty_chart()

    summary = pd.DataFrame(
        {
            "Status": ["Present", "Absent", "Leave"],
            "Days": [df["Present"].sum(), df["Absent"].sum(), df["Leave"].sum()],
        }
    )

    fig = px.pie(
        summary,
        names="Status",
        values="Days",
        color="Status",
        color_discrete_map=COLORS,
    )

    fig.update_traces(textinfo="percent+label")

    return style_chart(fig, title="Attendance Distribution", showlegend=True)


# ==========================================================
# DEPARTMENT SCORECARD
# ==========================================================


def department_scorecard(df):
    """
    Attendance percentage by department.
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

    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")

    fig.update_yaxes(range=[0, 100])

    return style_chart(fig, title="Department Performance")


# ==========================================================
# EXECUTIVE OVERTIME
# ==========================================================


def executive_overtime(df):
    """
    Overtime by department.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Department", as_index=False)
        .agg(Overtime=("OvTim", "sum"))
        .sort_values("Overtime", ascending=False)
    )

    fig = px.bar(
        summary,
        x="Department",
        y="Overtime",
        text="Overtime",
        color_discrete_sequence=[COLORS["OT"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Department Overtime")


# ==========================================================
# EXECUTIVE LEAVE
# ==========================================================


def executive_leave(df):
    """
    Leave by department.
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
# EXECUTIVE EMPLOYEE DISTRIBUTION
# ==========================================================


def executive_employee_distribution(df):
    """
    Employee distribution by department.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Department", as_index=False).agg(
        Employees=("EmpCode", "nunique")
    )

    fig = px.pie(summary, names="Department", values="Employees")

    fig.update_traces(textinfo="percent+label")

    return style_chart(fig, title="Employee Distribution", showlegend=True)


# ==========================================================
# COMPANY HEALTH PLACEHOLDER
# ==========================================================


def company_health():
    """
    Placeholder for future company health score.
    """

    return empty_chart("Company Health Score (Coming Soon)")


# ==========================================================
# EXECUTIVE SCORECARD PLACEHOLDER
# ==========================================================


def executive_scorecard():
    """
    Placeholder for future executive scorecard.
    """

    return empty_chart("Executive Scorecard (Coming Soon)")


# ==========================================================
# EXECUTIVE RISK MATRIX PLACEHOLDER
# ==========================================================


def executive_risk_matrix():
    """
    Placeholder for future executive risk matrix.
    """

    return empty_chart("Risk Matrix (Coming Soon)")
