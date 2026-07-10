"""
Attendance Charts

Reusable attendance visualizations for the
Neelkamal Attendance Dashboard.
"""

from utils.charts.common import pd, px, COLORS, style_chart, sort_months, empty_chart

# ==========================================================
# ATTENDANCE SUMMARY
# ==========================================================


def attendance_summary_chart(df):
    """
    Overall attendance percentage.
    """

    if df.empty:
        return empty_chart()

    present = df["Present"].sum()
    absent = df["Absent"].sum()

    total = present + absent

    if total == 0:
        return empty_chart("No attendance data available.")

    summary = pd.DataFrame(
        {
            "Status": ["Present", "Absent"],
            "Percentage": [
                round((present / total) * 100, 2),
                round((absent / total) * 100, 2),
            ],
        }
    )

    fig = px.pie(
        summary,
        names="Status",
        values="Percentage",
        hole=0.55,
        color="Status",
        color_discrete_map={"Present": COLORS["Present"], "Absent": COLORS["Absent"]},
    )

    fig.update_traces(
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{value:.2f}%<extra></extra>",
    )

    return style_chart(fig, title="Overall Attendance Percentage", showlegend=True)


# ==========================================================
# MONTHLY ATTENDANCE %
# ==========================================================


def attendance_trend_chart(summary):
    """
    Monthly Attendance Percentage.
    """

    if summary.empty:
        return empty_chart()

    summary = sort_months(summary)

    fig = px.line(summary, x="Month", y="AttendancePct", markers=True)

    fig.update_traces(line=dict(width=3, color=COLORS["Present"]), marker=dict(size=8))

    fig.update_yaxes(range=[0, 100], title="Attendance %")

    return style_chart(fig, title="Monthly Attendance Percentage")


# ==========================================================
# MONTHLY ATTENDANCE COUNTS
# ==========================================================


def attendance_count_chart(summary):
    """
    Monthly Present vs Absent vs Leave.
    """

    if summary.empty:
        return empty_chart()

    summary = sort_months(summary)

    chart = summary.melt(
        id_vars="Month",
        value_vars=["Present", "Absent", "Leave"],
        var_name="Status",
        value_name="Days",
    )

    fig = px.bar(
        chart,
        x="Month",
        y="Days",
        color="Status",
        color_discrete_map=COLORS,
        barmode="group",
    )

    return style_chart(fig, title="Monthly Attendance Comparison")


# ==========================================================
# MONTHLY PRESENT DAYS
# ==========================================================


def monthly_present_chart(summary):
    """
    Monthly Present Days.
    """

    if summary.empty:
        return empty_chart()

    summary = sort_months(summary)

    fig = px.bar(
        summary,
        x="Month",
        y="Present",
        text="Present",
        color_discrete_sequence=[COLORS["Present"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Monthly Present Days")


# ==========================================================
# MONTHLY ABSENT DAYS
# ==========================================================


def monthly_absent_chart(summary):
    """
    Monthly Absent Days.
    """

    if summary.empty:
        return empty_chart()

    summary = sort_months(summary)

    fig = px.bar(
        summary,
        x="Month",
        y="Absent",
        text="Absent",
        color_discrete_sequence=[COLORS["Absent"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Monthly Absent Days")


# ==========================================================
# MONTHLY LEAVE DAYS
# ==========================================================


def monthly_leave_chart(summary):
    """
    Monthly Leave Days.
    """

    if summary.empty:
        return empty_chart()

    summary = sort_months(summary)

    fig = px.bar(
        summary,
        x="Month",
        y="Leave",
        text="Leave",
        color_discrete_sequence=[COLORS["Leave"]],
    )

    fig.update_traces(textposition="outside")

    return style_chart(fig, title="Monthly Leave Days")


# ==========================================================
# ATTENDANCE PIE
# ==========================================================


def attendance_pie_chart(df):
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
# ATTENDANCE HEATMAP
# ==========================================================


def attendance_heatmap(summary):
    """
    Reserved for future heatmap implementation.
    """

    return empty_chart("Attendance Heatmap (Coming Soon)")


# ==========================================================
# ATTENDANCE GAUGE
# ==========================================================


def attendance_gauge(summary):
    """
    Reserved for executive dashboard.
    """

    return empty_chart("Attendance Gauge (Coming Soon)")
