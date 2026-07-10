import pandas as pd


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
# MONTHLY ATTENDANCE TREND
# ==========================================================


def monthly_attendance_trend(monthly_df):
    """
    Generate month-wise attendance summary.

    Parameters
    ----------
    monthly_df : pandas.DataFrame
        EmployeeMonthly dataset.

    Returns
    -------
    pandas.DataFrame
    """

    if monthly_df.empty:
        return pd.DataFrame(
            columns=["Month", "Present", "Absent", "Leave", "PaidDays", "AttendancePct"]
        )

    summary = monthly_df.groupby("Month", as_index=False).agg(
        {"Present": "sum", "Absent": "sum", "Leave": "sum", "PaidDays": "sum"}
    )

    total_days = summary["Present"] + summary["Absent"] + summary["Leave"]

    summary["AttendancePct"] = (summary["Present"] / total_days * 100).round(2)

    summary["Month"] = pd.Categorical(
        summary["Month"], categories=MONTH_ORDER, ordered=True
    )

    summary = summary.sort_values("Month").reset_index(drop=True)

    return summary
