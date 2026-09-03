"""
Employee Average Attendance Service

Builds employee-wise attendance averages from the existing
daily and monthly attendance datasets.

Daily data:
    - Avg In Time
    - Avg Out Time
    - Avg Working Hours

Monthly data:
    - Total Present
    - Absent

Important:
    Absent is taken directly from the uploaded monthly report.
    It is NOT calculated from working days or present days.
"""

import pandas as pd



# ==========================================================
# TIME CONVERSION HELPERS
# ==========================================================

def _time_to_minutes(value):
    """
    Convert an attendance time value to minutes from midnight.

    Supports:
        - datetime/time values
        - pandas Timestamp
        - strings such as HH:MM
        - strings such as HH:MM:SS
        - Excel time fractions

    Returns:
        float minutes or None for invalid/blank values.
    """

    if value is None or pd.isna(value):
        return None

    # Excel time fraction / numeric value
    if isinstance(value, (int, float)):
        value = float(value)

        if 0 <= value < 1:
            return value * 24 * 60

        return None

    # pandas Timestamp / datetime-like
    if isinstance(value, pd.Timestamp):
        return value.hour * 60 + value.minute + value.second / 60

    # Python datetime/time objects
    if hasattr(value, "hour") and hasattr(value, "minute"):
        return (
            value.hour * 60
            + value.minute
            + getattr(value, "second", 0) / 60
        )

    # String
    text = str(value).strip()

    if text in ["", "00:00", "00:00:00", "-", "nan"]:
        return None

    parsed = pd.to_datetime(
        text,
        errors="coerce"
    )

    if pd.isna(parsed):
        return None

    return (
        parsed.hour * 60
        + parsed.minute
        + parsed.second / 60
    )


def _work_hours_to_minutes(value):
    """
    Convert working-hours value to minutes.

    Supports values such as:
        08:30
        08:30:00
        8.5
        Excel time fractions

    Returns:
        float minutes or None.
    """

    if value is None or pd.isna(value):
        return None

    # Numeric values are interpreted as decimal hours,
    # except Excel-style fractions which represent a day.
    if isinstance(value, (int, float)):
        value = float(value)

        if 0 <= value < 1:
            return value * 24 * 60

        return value * 60

    text = str(value).strip()

    if text in ["", "00:00", "00:00:00", "-", "nan"]:
        return None

    # HH:MM or HH:MM:SS
    parts = text.split(":")

    if len(parts) in (2, 3):
        try:
            hours = float(parts[0])
            minutes = float(parts[1])

            seconds = (
                float(parts[2])
                if len(parts) == 3
                else 0
            )

            return hours * 60 + minutes + seconds / 60

        except (ValueError, TypeError):
            pass

    # Decimal hours
    try:
        return float(text) * 60
    except (ValueError, TypeError):
        return None


def _minutes_to_time(minutes):
    """
    Convert minutes from midnight to HH:MM.
    """

    if minutes is None or pd.isna(minutes):
        return ""

    minutes = float(minutes)

    # Keep result inside a 24-hour clock.
    minutes = minutes % (24 * 60)

    hours = int(minutes // 60)
    mins = int(round(minutes % 60))

    if mins == 60:
        hours = (hours + 1) % 24
        mins = 0

    return f"{hours:02d}:{mins:02d}"


def _minutes_to_duration(minutes):
    """
    Convert duration in minutes to HH:MM.
    """

    if minutes is None or pd.isna(minutes):
        return ""

    minutes = max(0, float(minutes))

    hours = int(minutes // 60)
    mins = int(round(minutes % 60))

    if mins == 60:
        hours += 1
        mins = 0

    return f"{hours:02d}:{mins:02d}"


# ==========================================================
# MAIN CALCULATION
# ==========================================================

def calculate_employee_averages(
    daily_df,
    monthly_df,
    year=None,
    month=None,
    department=None,
):
    """
    Build employee-wise attendance averages.

    Returns columns:

        EmpCode
        Name
        Department
        Designation
        Avg In Time
        Avg Out Time
        Avg Working Hours
        Total Present
        Absent
    """

    if daily_df is None:
        daily_df = pd.DataFrame()

    if monthly_df is None:
        monthly_df = pd.DataFrame()

    if not daily_df.empty and "Date" in daily_df.columns:

        daily_df["Date"] = pd.to_datetime(
            daily_df["Date"],
            errors="coerce"
        )

        if year is not None:
            daily_df = daily_df[
                daily_df["Date"].dt.year == int(year)
            ].copy()

        if month is not None:
            try:
                month_number = pd.to_datetime(
                    str(month),
                    format="%b"
                ).month
            except ValueError:
                try:
                    month_number = int(month)
                except (ValueError, TypeError):
                    month_number = None

            if month_number is not None:
                daily_df = daily_df[
                    daily_df["Date"].dt.month == month_number
                ].copy()

    # ------------------------------------------------------
    # PERIOD / DEPARTMENT FILTERS
    # ------------------------------------------------------

    if year is not None and not monthly_df.empty:
        monthly_df = monthly_df[
            pd.to_numeric(
                monthly_df["Year"],
                errors="coerce"
            ) == int(year)
        ].copy()

    if month is not None and not monthly_df.empty:
        monthly_df = monthly_df[
            monthly_df["Month"].astype(str).str.lower()
            == str(month).lower()
        ].copy()

    if department is not None and str(department).strip():
        if not daily_df.empty and "Department" in daily_df.columns:
            daily_df = daily_df[
                daily_df["Department"].astype(str).str.upper()
                == str(department).strip().upper()
            ].copy()

        if not monthly_df.empty and "Department" in monthly_df.columns:
            monthly_df = monthly_df[
                monthly_df["Department"].astype(str).str.upper()
                == str(department).strip().upper()
            ].copy()

    if daily_df.empty and monthly_df.empty:
        return pd.DataFrame(
            columns=[
                "EmpCode",
                "Name",
                "Department",
                "Designation",
                "Avg In Time",
                "Avg Out Time",
                "Avg Working Hours",
                "Total Present",
                "Absent",
            ]
        )

    # ------------------------------------------------------
    # DAILY DATA
    # ------------------------------------------------------

    daily = daily_df.copy()

    if not daily.empty:

        required_daily = [
            "EmpCode",
            "Name",
            "Department",
            "Designation",
            "InTime",
            "OutTime",
            "WorkHrs",
        ]

        for column in required_daily:
            if column not in daily.columns:
                daily[column] = ""

        daily["_InMinutes"] = daily["InTime"].apply(
            _time_to_minutes
        )

        daily["_OutMinutes"] = daily["OutTime"].apply(
            _time_to_minutes
        )

        daily["_WorkMinutes"] = daily["WorkHrs"].apply(
            _work_hours_to_minutes
        )

        daily_summary = (
            daily.groupby(
                [
                    "EmpCode",
                    "Name",
                    "Department",
                    "Designation",
                ],
                dropna=False
            )
            .agg(
                AvgInMinutes=("_InMinutes", "mean"),
                AvgOutMinutes=("_OutMinutes", "mean"),
                AvgWorkMinutes=("_WorkMinutes", "mean"),
            )
            .reset_index()
        )

    else:
        daily_summary = pd.DataFrame(
            columns=[
                "EmpCode",
                "Name",
                "Department",
                "Designation",
                "AvgInMinutes",
                "AvgOutMinutes",
                "AvgWorkMinutes",
            ]
        )

    # ------------------------------------------------------
    # MONTHLY DATA
    # ------------------------------------------------------

    monthly = monthly_df.copy()

    if not monthly.empty:

        required_monthly = [
            "EmpCode",
            "Name",
            "Department",
            "Designation",
            "Present",
            "Absent",
        ]

        for column in required_monthly:
            if column not in monthly.columns:
                monthly[column] = 0

        monthly["Present"] = pd.to_numeric(
            monthly["Present"],
            errors="coerce"
        ).fillna(0)

        monthly["Absent"] = pd.to_numeric(
            monthly["Absent"],
            errors="coerce"
        ).fillna(0)

        monthly_summary = (
            monthly.groupby(
                [
                    "EmpCode",
                    "Name",
                    "Department",
                    "Designation",
                ],
                dropna=False
            )
            .agg(
                TotalPresent=("Present", "sum"),
                Absent=("Absent", "sum"),
            )
            .reset_index()
        )

    else:
        monthly_summary = pd.DataFrame(
            columns=[
                "EmpCode",
                "Name",
                "Department",
                "Designation",
                "TotalPresent",
                "Absent",
            ]
        )

    # ------------------------------------------------------
    # COMBINE DAILY + MONTHLY
    # ------------------------------------------------------

    if daily_summary.empty:
        result = monthly_summary.copy()

    elif monthly_summary.empty:
        result = daily_summary.copy()

    else:
        result = pd.merge(
            daily_summary,
            monthly_summary,
            on=[
                "EmpCode",
                "Name",
                "Department",
                "Designation",
            ],
            how="outer",
        )

    # ------------------------------------------------------
    # FORMAT RESULT
    # ------------------------------------------------------

    if result.empty:
        return pd.DataFrame(
            columns=[
                "EmpCode",
                "Name",
                "Department",
                "Designation",
                "Avg In Time",
                "Avg Out Time",
                "Avg Working Hours",
                "Total Present",
                "Absent",
            ]
        )

    result["Avg In Time"] = result[
        "AvgInMinutes"
    ].apply(_minutes_to_time)

    result["Avg Out Time"] = result[
        "AvgOutMinutes"
    ].apply(_minutes_to_time)

    result["Avg Working Hours"] = result[
        "AvgWorkMinutes"
    ].apply(_minutes_to_duration)

    result["Total Present"] = pd.to_numeric(
        result.get("TotalPresent", 0),
        errors="coerce"
    ).fillna(0)

    result["Absent"] = pd.to_numeric(
        result.get("Absent", 0),
        errors="coerce"
    ).fillna(0)

    result = result[
        [
            "EmpCode",
            "Name",
            "Department",
            "Designation",
            "Avg In Time",
            "Avg Out Time",
            "Avg Working Hours",
            "Total Present",
            "Absent",
        ]
    ]

    result = result.sort_values(
        ["Department", "EmpCode"],
        na_position="last"
    ).reset_index(drop=True)

    return result

# ==========================================================
# DATA ACCESS WRAPPER
# ==========================================================

def get_employee_average_data(
    year=None,
    month=None,
    department=None,
):
    """
    Load attendance data for the current user and return
    employee-wise averages.

    Optional filters:
        year
        month
        department
    """

    from utils.data_access import (
        load_daily_data,
        load_monthly_data,
    )

    daily = load_daily_data()
    monthly = load_monthly_data()

    return calculate_employee_averages(
        daily,
        monthly,
        year=year,
        month=month,
        department=department,
    )