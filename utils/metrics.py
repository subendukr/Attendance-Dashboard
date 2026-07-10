import pandas as pd


# =====================================================
# ATTENDANCE STATUS GROUPS
# =====================================================

PRESENT_STATUS = {"P", "P-LT", "WFH", "OD"}

ABSENT_STATUS = {"A"}

LEAVE_STATUS = {"L"}

HOLIDAY_STATUS = {"H", "HL"}


# =====================================================
# TIME HELPER FUNCTIONS
# =====================================================


def time_to_minutes(time_str):
    """
    Convert HH:MM string into total minutes.
    Returns None for invalid values.
    """

    if pd.isna(time_str):
        return None

    time_str = str(time_str).strip()

    if time_str in ["", "00:00", "-", "nan"]:
        return None

    try:
        hours, minutes = map(int, time_str.split(":"))

        return hours * 60 + minutes

    except Exception:
        return None


def minutes_to_time(total_minutes):
    """
    Convert total minutes back to HH:MM.
    """

    if total_minutes is None:
        return "-"

    total_minutes = int(round(total_minutes))

    hours = total_minutes // 60
    minutes = total_minutes % 60

    return f"{hours:02d}:{minutes:02d}"


def average_time(series):
    """
    Calculate arithmetic mean of HH:MM values.
    """

    minutes = series.apply(time_to_minutes).dropna()

    if minutes.empty:
        return "-"

    return minutes_to_time(minutes.mean())


def total_time(series):
    """
    Calculate total duration of HH:MM values.
    """

    minutes = series.apply(time_to_minutes).dropna()

    if minutes.empty:
        return "-"

    return minutes_to_time(minutes.sum())


# =====================================================
# DASHBOARD METRICS
# =====================================================


def dashboard_metrics(df):
    """
    Calculate dashboard KPIs from EmployeeMonthly.xlsx
    """

    if df.empty:
        return {
            "employees": 0,
            "present": 0,
            "absent": 0,
            "leave": 0,
            "holiday": 0,
            "weekly_off": 0,
            "paid_days": 0,
            "attendance_pct": 0,
        }

    employees = df["EmpCode"].nunique()

    present = df.get("Present", pd.Series(dtype=float)).sum()

    absent = df.get("Absent", pd.Series(dtype=float)).sum()

    leave = df.get("Leave", pd.Series(dtype=float)).sum()

    holiday = df.get("HL", pd.Series(dtype=float)).sum()

    weekly_off = df.get("WO", pd.Series(dtype=float)).sum()

    paid_days = df.get("PaidDays", pd.Series(dtype=float)).sum()

    total_days = present + absent + leave

    attendance_pct = (present / total_days) * 100 if total_days > 0 else 0

    return {
        "employees": employees,
        "present": present,
        "absent": absent,
        "leave": leave,
        "holiday": holiday,
        "weekly_off": weekly_off,
        "paid_days": paid_days,
        "attendance_pct": round(attendance_pct, 2),
    }


# =====================================================
# EMPLOYEE SEARCH METRICS
# =====================================================


def employee_metrics(df):
    """
    Calculate Employee Search KPIs.
    """

    if df.empty:
        return {
            "present": 0,
            "absent": 0,
            "leave": 0,
            "holiday": 0,
            "attendance_pct": 0,
        }

    status = df["Status"].fillna("").astype(str).str.strip().str.upper()

    present = (status.isin(PRESENT_STATUS)).sum()

    absent = (status.isin(ABSENT_STATUS)).sum()

    leave = (status.isin(LEAVE_STATUS)).sum()

    holiday = (status.isin(HOLIDAY_STATUS)).sum()

    total_days = present + absent + leave

    attendance_pct = (present / total_days) * 100 if total_days > 0 else 0

    return {
        "present": present,
        "absent": absent,
        "leave": leave,
        "holiday": holiday,
        "attendance_pct": round(attendance_pct, 2),
    }


# =====================================================
# TIME METRICS
# =====================================================


def time_metrics(df):
    """
    Calculate average In Time,
    Out Time,
    Work Hours,
    and Overtime.
    """

    if df.empty:
        return {"avg_in": "-", "avg_out": "-", "avg_work": "-", "ot": "-"}

    avg_in = average_time(df["InTime"])

    avg_out = average_time(df["OutTime"])

    avg_work = average_time(df["WorkHrs"])

    total_ot = total_time(df["OTHrs"])

    return {"avg_in": avg_in, "avg_out": avg_out, "avg_work": avg_work, "ot": total_ot}
