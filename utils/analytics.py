import pandas as pd


# ==========================================================
# Time Conversion Helpers
# ==========================================================


def time_to_minutes(time_str):
    """
    Convert HH:MM string to total minutes.

    Examples:
        01:30 -> 90
        10:45 -> 645
        00:00 -> 0
        "" or NaN -> 0
    """

    if pd.isna(time_str):
        return 0

    time_str = str(time_str).strip()

    if time_str == "":
        return 0

    try:
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes

    except Exception:
        return 0


def minutes_to_time(total_minutes):
    """
    Convert total minutes back to HH:MM format.

    Examples:
        90 -> 01:30
        645 -> 10:45
        0 -> 00:00
    """

    total_minutes = int(total_minutes)

    hours = total_minutes // 60
    minutes = total_minutes % 60

    return f"{hours:02d}:{minutes:02d}"


# ==========================================================
# Attendance Trend
# ==========================================================


def attendance_trend(df):

    trend = (
        df.groupby(["Year", "Month"])
        .agg({"Present": "sum", "Absent": "sum", "Leave": "sum"})
        .reset_index()
    )

    return trend


# ==========================================================
# Department Summary
# ==========================================================


def department_summary(df):

    summary = (
        df.groupby("Department")
        .agg(
            Employees=("EmpCode", "nunique"),
            Present=("Present", "sum"),
            Absent=("Absent", "sum"),
            Leave=("Leave", "sum"),
        )
        .reset_index()
    )

    return summary


# ==========================================================
# Designation Summary
# ==========================================================


def designation_summary(df):

    summary = (
        df.groupby("Designation")
        .agg(
            Employees=("EmpCode", "nunique"),
            Present=("Present", "sum"),
            Absent=("Absent", "sum"),
            Leave=("Leave", "sum"),
        )
        .reset_index()
    )

    return summary


# ==========================================================
# Shift Summary
# ==========================================================


def shift_summary(df):

    summary = df.groupby("Shift").size().reset_index(name="Records")

    return summary


# ==========================================================
# Status Distribution
# ==========================================================


def status_distribution(df):

    summary = df.groupby("Status").size().reset_index(name="Count")

    return summary


# ==========================================================
# Top Absentees
# ==========================================================


def top_absentees(df, n=10):

    summary = df.groupby(["EmpCode", "Name"])["Absent"].sum().reset_index()

    summary = summary.sort_values("Absent", ascending=False)

    return summary.head(n)


# ==========================================================
# Overtime Summary
# ==========================================================


def overtime_summary(df):

    overtime = df.copy()

    overtime["OT_Minutes"] = overtime["OTHrs"].apply(time_to_minutes)

    summary = (
        overtime.groupby(["EmpCode", "Name"])
        .agg(Total_OT_Minutes=("OT_Minutes", "sum"))
        .reset_index()
    )

    summary["Total_OT"] = summary["Total_OT_Minutes"].apply(minutes_to_time)

    summary = summary.drop(columns=["Total_OT_Minutes"])

    return summary


# ==========================================================
# Department Performance
# ==========================================================


def department_performance(df):

    summary = (
        df.groupby("Department")
        .agg(
            Employees=("EmpCode", "nunique"),
            Present=("Present", "sum"),
            Absent=("Absent", "sum"),
            Leave=("Leave", "sum"),
            PaidDays=("PaidDays", "mean"),
        )
        .reset_index()
    )

    total = summary["Present"] + summary["Absent"] + summary["Leave"]

    summary["Attendance %"] = (
        summary["Present"].div(total.replace(0, pd.NA)).fillna(0) * 100
    ).round(2)

    return summary


# ==========================================================
# Designation Performance
# ==========================================================


def designation_performance(df):

    summary = (
        df.groupby("Designation")
        .agg(
            Employees=("EmpCode", "nunique"),
            Present=("Present", "sum"),
            Absent=("Absent", "sum"),
            Leave=("Leave", "sum"),
            PaidDays=("PaidDays", "mean"),
        )
        .reset_index()
    )

    total = summary["Present"] + summary["Absent"] + summary["Leave"]

    summary["Attendance %"] = (
        summary["Present"].div(total.replace(0, pd.NA)).fillna(0) * 100
    ).round(2)

    return summary
