import pandas as pd


# =====================================================
# EMPLOYEE PROFILE
# =====================================================


def employee_profile(df, empcode):

    emp = df[df["EmpCode"].astype(str).str.upper() == str(empcode).upper()]

    if emp.empty:
        return {}

    row = emp.iloc[0]

    return {
        "EmpCode": row["EmpCode"],
        "Name": row["Name"],
        "Company": row["Company"],
        "Department": row["Department"],
        "Designation": row["Designation"],
        "Shift": row["Shift"],
    }


# =====================================================
# AVAILABLE YEARS
# =====================================================


def employee_available_years(df, empcode):

    emp = df[df["EmpCode"].astype(str).str.upper() == str(empcode).upper()]

    years = sorted(emp["Date"].dt.year.unique())

    return years


# =====================================================
# AVAILABLE MONTHS
# =====================================================


def employee_available_months(df, empcode, year):

    emp = df[
        (df["EmpCode"].astype(str).str.upper() == str(empcode).upper())
        & (df["Date"].dt.year == year)
    ]

    month_order = [
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

    months = [m for m in month_order if m in emp["Date"].dt.strftime("%b").unique()]

    return months


# =====================================================
# ATTENDANCE CALENDAR
# =====================================================


def employee_calendar(df):

    emp = df.sort_values("Date")

    calendar = pd.DataFrame(
        [emp["Status"].values], columns=[d.strftime("%d") for d in emp["Date"]]
    )

    return calendar


# =====================================================
# MONTHLY HISTORY
# =====================================================


def employee_history(df, empcode):

    emp = df[df["EmpCode"].astype(str).str.upper() == str(empcode).upper()]

    history = emp.groupby(emp["Date"].dt.to_period("M")).agg(
        {"Status": lambda x: (x == "P").sum()}
    )

    history.columns = ["Present"]

    history = history.reset_index()

    history["Date"] = history["Date"].astype(str)

    return history


# =====================================================
# DAILY LOG
# =====================================================


def employee_daily_log(df):

    columns = ["Date", "Status", "Shift", "InTime", "OutTime", "WorkHrs", "OTHrs"]

    log = df[columns]

    log = log.sort_values("Date")

    log.reset_index(drop=True, inplace=True)

    return log
