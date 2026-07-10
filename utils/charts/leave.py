"""
Leave Charts

Reusable leave visualizations for the
Neelkamal Attendance Dashboard.
"""

from utils.charts.common import pd, px, COLORS, style_chart, sort_months, empty_chart


# ==========================================================
# MONTHLY LEAVE
# ==========================================================


def monthly_leave_chart(df):
    """
    Total leave by month.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Month", as_index=False).agg(Leave=("Leave", "sum"))

    summary = sort_months(summary)

    fig = px.bar(
        summary,
        x="Month",
        y="Leave",
        text="Leave",
        color_discrete_sequence=[COLORS["Leave"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Monthly Leave")


# ==========================================================
# MONTHLY LEAVE TREND
# ==========================================================


def leave_trend_chart(df):
    """
    Monthly leave trend.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Month", as_index=False).agg(Leave=("Leave", "sum"))

    summary = sort_months(summary)

    fig = px.line(summary, x="Month", y="Leave", markers=True)

    fig.update_traces(line=dict(width=3, color=COLORS["Leave"]), marker=dict(size=8))

    return style_chart(fig, title="Monthly Leave Trend")


# ==========================================================
# DEPARTMENT LEAVE
# ==========================================================


def department_leave_chart(df):
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
# EMPLOYEE LEAVE
# ==========================================================


def employee_leave_chart(df):
    """
    Top employees by leave.
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
# TOP LEAVE EMPLOYEES
# ==========================================================


def top_leave_chart(df, top_n=10):
    """
    Top leave employees.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Name", as_index=False)
        .agg(Leave=("Leave", "sum"))
        .sort_values("Leave", ascending=False)
        .head(top_n)
    )

    fig = px.bar(
        summary,
        x="Name",
        y="Leave",
        text="Leave",
        color_discrete_sequence=[COLORS["Leave"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title=f"Top {top_n} Employees by Leave")


# ==========================================================
# LEAVE DISTRIBUTION
# ==========================================================


def leave_distribution_chart(df):
    """
    Leave distribution by employee.
    """

    if df.empty:
        return empty_chart()

    bins = [0, 2, 5, 10, 15, 20, float("inf")]

    labels = ["0-2", "3-5", "6-10", "11-15", "16-20", "20+"]

    summary = df.groupby("Name", as_index=False).agg(Leave=("Leave", "sum"))

    summary["Range"] = pd.cut(summary["Leave"], bins=bins, labels=labels)

    distribution = summary["Range"].value_counts().sort_index().reset_index()

    distribution.columns = ["Range", "Employees"]

    fig = px.bar(
        distribution,
        x="Range",
        y="Employees",
        text="Employees",
        color_discrete_sequence=[COLORS["Leave"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Leave Distribution")


# ==========================================================
# LEAVE SHARE
# ==========================================================


def leave_department_pie(df):
    """
    Department-wise leave share.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Department", as_index=False).agg(Leave=("Leave", "sum"))

    fig = px.pie(summary, names="Department", values="Leave")

    fig.update_traces(textinfo="percent+label")

    return style_chart(fig, title="Department Leave Share", showlegend=True)


# ==========================================================
# LEAVE HEATMAP
# ==========================================================


def leave_heatmap(df):
    """
    Reserved for future implementation.
    """

    return empty_chart("Leave Heatmap (Coming Soon)")


# ==========================================================
# LEAVE CALENDAR
# ==========================================================


def leave_calendar(df):
    """
    Reserved for future implementation.
    """

    return empty_chart("Leave Calendar (Coming Soon)")


# ==========================================================
# LEAVE GAUGE
# ==========================================================


def leave_gauge(df):
    """
    Reserved for Executive Dashboard.
    """

    return empty_chart("Leave KPI Gauge (Coming Soon)")
