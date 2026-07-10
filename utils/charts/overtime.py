"""
Overtime Charts

Reusable overtime visualizations for the
Neelkamal Attendance Dashboard.
"""

from utils.charts.common import pd, px, COLORS, style_chart, sort_months, empty_chart


# ==========================================================
# MONTHLY OVERTIME
# ==========================================================


def monthly_ot_chart(df):
    """
    Total overtime by month.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Month", as_index=False).agg(Overtime=("OvTim", "sum"))

    summary = sort_months(summary)

    fig = px.bar(
        summary,
        x="Month",
        y="Overtime",
        text="Overtime",
        color_discrete_sequence=[COLORS["OT"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Monthly Overtime")


# ==========================================================
# DEPARTMENT OVERTIME
# ==========================================================


def department_ot_chart(df):
    """
    Department-wise overtime.
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
# EMPLOYEE OVERTIME
# ==========================================================


def employee_ot_chart(df):
    """
    Top employees by overtime.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Name", as_index=False)
        .agg(Overtime=("OvTim", "sum"))
        .sort_values("Overtime", ascending=False)
        .head(20)
    )

    fig = px.bar(
        summary,
        x="Name",
        y="Overtime",
        text="Overtime",
        color_discrete_sequence=[COLORS["OT"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Top Employees by Overtime")


# ==========================================================
# TOP OVERTIME EMPLOYEES
# ==========================================================


def top_ot_chart(df, top_n=10):
    """
    Top overtime employees.
    """

    if df.empty:
        return empty_chart()

    summary = (
        df.groupby("Name", as_index=False)
        .agg(Overtime=("OvTim", "sum"))
        .sort_values("Overtime", ascending=False)
        .head(top_n)
    )

    fig = px.bar(
        summary,
        x="Name",
        y="Overtime",
        text="Overtime",
        color_discrete_sequence=[COLORS["OT"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title=f"Top {top_n} Overtime Employees")


# ==========================================================
# OVERTIME DISTRIBUTION
# ==========================================================


def ot_distribution_chart(df):
    """
    Overtime distribution.
    """

    if df.empty:
        return empty_chart()

    bins = [0, 10, 20, 40, 60, 80, 100, float("inf")]

    labels = ["0-10", "11-20", "21-40", "41-60", "61-80", "81-100", "100+"]

    summary = df.groupby("Name", as_index=False).agg(Overtime=("OvTim", "sum"))

    summary["Range"] = pd.cut(summary["Overtime"], bins=bins, labels=labels)

    distribution = summary["Range"].value_counts().sort_index().reset_index()

    distribution.columns = ["Range", "Employees"]

    fig = px.bar(
        distribution,
        x="Range",
        y="Employees",
        text="Employees",
        color_discrete_sequence=[COLORS["OT"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Overtime Distribution")


# ==========================================================
# MONTHLY OT TREND
# ==========================================================


def ot_trend_chart(df):
    """
    Monthly overtime trend.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Month", as_index=False).agg(Overtime=("OvTim", "sum"))

    summary = sort_months(summary)

    fig = px.line(summary, x="Month", y="Overtime", markers=True)

    fig.update_traces(line=dict(width=3, color=COLORS["OT"]), marker=dict(size=8))

    return style_chart(fig, title="Monthly Overtime Trend")


# ==========================================================
# OVERTIME PIE
# ==========================================================


def ot_department_pie(df):
    """
    Department overtime share.
    """

    if df.empty:
        return empty_chart()

    summary = df.groupby("Department", as_index=False).agg(Overtime=("OvTim", "sum"))

    fig = px.pie(summary, names="Department", values="Overtime")

    fig.update_traces(textinfo="percent+label")

    return style_chart(fig, title="Department Overtime Share", showlegend=True)


# ==========================================================
# OVERTIME HEATMAP
# ==========================================================


def ot_heatmap(df):
    """
    Reserved for future implementation.
    """

    return empty_chart("Overtime Heatmap (Coming Soon)")


# ==========================================================
# OVERTIME GAUGE
# ==========================================================


def ot_gauge(df):
    """
    Reserved for Executive Dashboard.
    """

    return empty_chart("Overtime Gauge (Coming Soon)")
