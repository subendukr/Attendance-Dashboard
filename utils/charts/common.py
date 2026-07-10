"""
Common Chart Utilities

This module provides shared styling, formatting and helper
functions used across all chart modules.

Every chart should import from this module instead of
defining its own colours or layouts.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px  # noqa: F401


# ==========================================================
# MONTH ORDER
# ==========================================================

MONTH_ORDER = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


# ==========================================================
# CORPORATE COLOR PALETTE
# ==========================================================

COLORS = {
    "Present": "#16A34A",  # Green
    "Absent": "#DC2626",  # Red
    "Leave": "#F59E0B",  # Amber
    "Holiday": "#2563EB",  # Blue
    "Late": "#EA580C",  # Orange
    "OT": "#7C3AED",  # Purple
    "Department": "#0891B2",  # Cyan
    "Employee": "#0F766E",  # Teal
    "PaidDays": "#2563EB",
    "WorkHours": "#4F46E5",
}


# ==========================================================
# CORPORATE FONT
# ==========================================================

FONT = dict(family="Arial", size=13, color="#1F2937")


# ==========================================================
# CORPORATE TEMPLATE
# ==========================================================

DEFAULT_TEMPLATE = "plotly_white"


# ==========================================================
# STYLE CHART
# ==========================================================


def style_chart(fig, title=None, height=420, showlegend=False):
    """
    Apply Neelkamal Dashboard styling
    to every Plotly figure.
    """

    fig.update_layout(
        template=DEFAULT_TEMPLATE,
        height=height,
        autosize=True,
        showlegend=showlegend,
        font=FONT,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=60, b=20),
        title=dict(
            text=title,
            x=0.02,
            xanchor="left",
            font=dict(size=20, family="Segoe UI", color="#1E40AF"),
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#2563Eb",
            font=dict(color="#1E293B", size=13, family="Segoe UI"),
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        showline=True,
        linewidth=1,
        linecolor="#D1D5DB",
        # Tick labels (Present, Absent, HR, etc.)
        tickfont=dict(size=13, family="Arial", color="#475569"),
        # Axis title (Status, Department, Month)
        title_font=dict(size=15, family="Arial", color="#1E3A8A"),
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E5E7EB",
        zeroline=False,
        showline=True,
        linewidth=1,
        linecolor="#D1D5DB",
        # Tick labels (0, 10, 20, etc.)
        tickfont=dict(size=13, family="Arial", color="#475569"),
        # Axis title (Days,Present, Attendance %)
        title_font=dict(size=15, family="Arial", color="#1E3A8A"),
    )

    return fig


# ==========================================================
# SORT MONTHS
# ==========================================================


def sort_months(df):
    """
    Sort a dataframe by calendar month.
    """

    if "Month" not in df.columns:
        return df

    df = df.copy()

    df["Month"] = pd.Categorical(df["Month"], categories=MONTH_ORDER, ordered=True)

    return df.sort_values("Month").reset_index(drop=True)


# ==========================================================
# FORMAT NUMBER
# ==========================================================


def format_number(value):
    """
    Format integers using thousand separators.
    """

    try:
        return f"{int(value):,}"

    except Exception:
        return value


# ==========================================================
# FORMAT PERCENTAGE
# ==========================================================


def format_percentage(value):
    """
    Format percentage values.
    """

    try:
        return f"{float(value):.2f}%"

    except Exception:
        return value


# ==========================================================
# FORMAT HOURS
# ==========================================================


def format_hours(minutes):
    """
    Convert minutes into HH:MM format.

    Example
    -------
    185 -> 03:05
    """

    if minutes is None:
        return "-"

    try:
        minutes = int(round(minutes))

    except Exception:
        return "-"

    hours = minutes // 60

    mins = minutes % 60

    return f"{hours:02d}:{mins:02d}"


# ==========================================================
# EMPTY CHART
# ==========================================================


def empty_chart(message="No data available"):
    """
    Return a placeholder figure when
    no chart data exists.
    """

    fig = go.Figure()

    fig.add_annotation(
        text=message, x=0.5, y=0.5, showarrow=False, font=dict(size=18, color="#6B7280")
    )

    fig.update_xaxes(visible=False)

    fig.update_yaxes(visible=False)

    fig.update_layout(
        template=DEFAULT_TEMPLATE,
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    return fig
