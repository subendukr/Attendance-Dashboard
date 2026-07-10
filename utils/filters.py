# ==========================================================
# MONTHLY FILTERS
# ==========================================================


def filter_monthly(
    df,
    year=None,
    month=None,
    company=None,
    department=None,
    designation=None,
    empcode=None,
):

    filtered = df.copy()

    if year is not None:
        filtered = filtered[filtered["Year"] == year]

    if month is not None:
        filtered = filtered[
            filtered["Month"].astype(str).str.upper() == str(month).upper()
        ]

    if company is not None and len(company) > 0:
        filtered = filtered[filtered["Company"].isin(company)]

    if department:
        filtered = filtered[filtered["Department"].isin(department)]

    if designation:
        filtered = filtered[filtered["Designation"].isin(designation)]

    if empcode:
        filtered = filtered[
            filtered["EmpCode"]
            .astype(str)
            .str.strip()
            .str.upper()
            .str.contains(str(empcode).strip().upper(), na=False)
        ]

    filtered = filtered.sort_values("EmpCode").reset_index(drop=True)

    return filtered


# ==========================================================
# DAILY FILTERS
# ==========================================================


def filter_daily(
    df,
    empcode=None,
    year=None,
    month=None,
    company=None,
    department=None,
    designation=None,
    status=None,
    shift=None,
):

    filtered = df.copy()

    if empcode:
        filtered = filtered[
            filtered["EmpCode"].astype(str).str.strip().str.upper()
            == str(empcode).strip().upper()
        ]

    if year is not None:
        filtered = filtered[filtered["Date"].dt.year == year]

    if month is not None:
        filtered = filtered[
            filtered["Date"].dt.strftime("%b").str.upper() == str(month).upper()
        ]

    if company is not None and len(company) > 0:
        filtered = filtered[filtered["Company"].isin(company)]

    if department:
        filtered = filtered[filtered["Department"].isin(department)]

    if designation:
        filtered = filtered[filtered["Designation"].isin(designation)]

    if status is not None:
        filtered = filtered[
            filtered["Status"].astype(str).str.upper() == str(status).upper()
        ]

    if shift is not None:
        filtered = filtered[
            filtered["Shift"].astype(str).str.upper() == str(shift).upper()
        ]

    filtered = filtered.sort_values("Date").reset_index(drop=True)

    return filtered
