import pandas as pd
from datetime import datetime
from pathlib import Path
from utils.company_detector import detect_company

# ==========================================================
# VALUE CLEANER
# ==========================================================


def clean_value(value):
    """
    Convert Excel cell values into clean strings.

    Returns:
        "" for NaN
        Trimmed string otherwise
    """

    if pd.isna(value):
        return ""

    return str(value).strip()


# ==========================================================
# FIND REPORT DATE
# ==========================================================


def find_report_date(df):
    """
    Locate the Report Date anywhere
    in the upper-left section of the sheet.

    Expected format:

    Report Date : 01-05-2025 To 31-05-2025
    """

    search_rows = min(10, len(df))
    search_cols = min(10, len(df.columns))

    for r in range(search_rows):
        for c in range(search_cols):
            text = clean_value(df.iloc[r, c])

            if "Report Date" in text:
                try:
                    start = text.split(":")[1].split("To")[0].strip()

                    return datetime.strptime(start, "%d-%m-%Y")

                except Exception:
                    continue

    raise ValueError("Report Date not found.")


# ==========================================================
# FIND DEPARTMENT
# ==========================================================


def find_department(df):
    """
    Locate the Department line.

    Example:

    Department :- CCM
    """

    search_rows = min(15, len(df))
    search_cols = min(8, len(df.columns))

    for r in range(search_rows):
        for c in range(search_cols):
            text = clean_value(df.iloc[r, c])

            if "Department" in text:
                return (
                    text.replace("Department :-", "").replace("Department:", "").strip()
                )

    return ""


# ==========================================================
# FIND EMPLOYEE START ROW
# ==========================================================


def find_employee_start_row(df):
    """
    Find the row immediately after
    the EmpCode header.

    Returns
    -------
    Integer row number

    Example

    Row 5 : EmpCode
    Row 6 : Employee

    Returns 6
    """

    for r in range(len(df)):
        row = df.iloc[r].astype(str).str.strip()

        if row.str.contains("EmpCode", case=False, na=False).any():
            return r + 1

    return None


# ==========================================================
# ITERATE EMPLOYEES
# ==========================================================


def iter_employees(df):
    """
    Yields (empcode, name, designation, i) for each employee in the sheet.
    """
    start_row = find_employee_start_row(df)
    if start_row is None:
        return

    i = start_row
    while i < len(df):
        if i + 7 >= len(df):
            break

        empcode = clean_value(df.iloc[i, 2])

        if empcode == "" or empcode.upper() == "EMPCODE":
            i += 1
            continue

        name = clean_value(df.iloc[i, 3])
        designation = clean_value(df.iloc[i, 9])
        
        yield empcode, name, designation, i
        i += 10



# ==========================================================
# FIND DAY COLUMNS
# ==========================================================


def get_day_columns(df, row_number):
    """
    Locate all calendar day columns.

    Example

    1 2 3 4 ... 31

    Returns

    List of column indexes
    """

    if row_number >= len(df):
        return []

    row = df.iloc[row_number]

    columns = []

    for col in range(len(row)):
        value = row[col]

        if pd.isna(value):
            continue

        try:
            day = int(value)

        except Exception:
            continue

        if 1 <= day <= 31:
            columns.append(col)

    return columns


# ==========================================================
# SHEET VALIDATION
# ==========================================================


def is_valid_sheet(df):
    """
    Check whether the worksheet
    contains attendance data.

    A valid sheet must contain

        Report Date

    and

        Department
    """

    try:
        _ = find_report_date(df)

        department = find_department(df)

        return department != ""

    except Exception:
        return False


# ==========================================================
# DAILY DATASET
# ==========================================================


def extract_daily(filepath):
    """
    Extract employee-wise daily attendance
    from every worksheet in the workbook.
    """

    xls = pd.ExcelFile(filepath)

    print("\n" + "=" * 70)
    print("Workbook contains the following sheets:")
    print("=" * 70)

    for i, sheet in enumerate(xls.sheet_names, start=1):
        print(f"{i}. {sheet}")

    print("=" * 70)
    print()

    records = []

    # ------------------------------------------------------
    # Process each worksheet
    # ------------------------------------------------------

    for sheet in xls.sheet_names:
        print("\n" + "=" * 60)
        print(f"Processing Sheet : {sheet}")
        print("=" * 60)

        try:
            df = pd.read_excel(filepath, sheet_name=sheet, header=None)

            # ---------------------------------------------
            # Debug Information
            # ---------------------------------------------

            try:
                report_date = find_report_date(df)

                print(f"✓ Report Date       : {report_date}")

            except Exception as e:
                print(f"✗ Report Date Error : {e}")

            try:
                department = find_department(df)

                print(f"✓ Department        : {department}")

            except Exception as e:
                print(f"✗ Department Error  : {e}")

                department = ""

            start_row = find_employee_start_row(df)

            print(f"✓ Employee Row      : {start_row}")

            # ---------------------------------------------
            # Validate Sheet
            # ---------------------------------------------

            if not is_valid_sheet(df):
                print(f"✗ Skipping '{sheet}' (Invalid Attendance Sheet)")
                continue

            year = report_date.year
            month = report_date.month

            sheet_records = 0

            # ---------------------------------------------
            # Employee Loop
            # ---------------------------------------------

            for empcode, name, designation, i in iter_employees(df):
                day_columns = get_day_columns(df, i + 1)

                if not day_columns:
                    continue

                # -----------------------------------------
                # One Record Per Day
                # -----------------------------------------

                for col in day_columns:
                    try:
                        day = int(df.iloc[i + 1, col])
                        attendance_date = pd.Timestamp(year, month, day)
                    except Exception:
                        continue

                    records.append(
                        {
                            "EmpCode": empcode,
                            "Name": name,
                            "Department": department,
                            "Designation": designation,
                            "Date": attendance_date,
                            "InTime": clean_value(df.iloc[i + 2, col]),
                            "OutTime": clean_value(df.iloc[i + 3, col]),
                            "WorkHrs": clean_value(df.iloc[i + 4, col]),
                            "OTHrs": clean_value(df.iloc[i + 5, col]),
                            "Status": clean_value(df.iloc[i + 6, col]),
                            "Shift": clean_value(df.iloc[i + 7, col]),
                        }
                    )

                    sheet_records += 1

            print(f"✓ Records Extracted : {sheet_records}")

        except Exception as e:
            print(f"ERROR while processing '{sheet}'")

            print(e)

            continue

    # =====================================================
    # Final Dataset
    # =====================================================

    daily = pd.DataFrame(records)

    if daily.empty:
        print("\nNo daily attendance records extracted.\n")

        return daily

    daily = (
        daily.drop_duplicates(subset=["EmpCode", "Date"])
        .sort_values(["EmpCode", "Date"])
        .reset_index(drop=True)
    )

    print()

    print("=" * 70)
    print(f"Total Daily Records : {len(daily)}")
    print("=" * 70)

    return daily


# ==========================================================
# MONTHLY DATASET
# ==========================================================


def extract_monthly(filepath):
    """
    Extract employee-wise monthly attendance
    summary from every worksheet.
    """

    xls = pd.ExcelFile(filepath)

    records = []

    for sheet in xls.sheet_names:
        print(f"Processing sheet : {sheet}")

        df = pd.read_excel(filepath, sheet_name=sheet, header=None)

        # ---------------------------------------------
        # Skip invalid sheets
        # ---------------------------------------------

        if not is_valid_sheet(df):
            print(f"Skipped : {sheet}")
            continue

        department = find_department(df)
        report_date = find_report_date(df)
        year = report_date.year
        month = report_date.strftime("%b")

        sheet_records = 0

        for empcode, name, designation, i in iter_employees(df):
            records.append(
                {
                    "EmpCode": empcode,
                    "Name": name,
                    "Department": department,
                    "Designation": designation,
                    "Year": year,
                    "Month": month,
                    "Present": pd.to_numeric(df.iloc[i, 14], errors="coerce"),
                    "HL": pd.to_numeric(df.iloc[i, 17], errors="coerce"),
                    "WO": pd.to_numeric(df.iloc[i, 19], errors="coerce"),
                    "Absent": pd.to_numeric(df.iloc[i, 21], errors="coerce"),
                    "Leave": pd.to_numeric(df.iloc[i, 23], errors="coerce"),
                    "PaidDays": pd.to_numeric(df.iloc[i, 27], errors="coerce"),
                    "LateHrs": clean_value(df.iloc[i, 30]),
                    "WorkHrs": clean_value(df.iloc[i, 34]),
                    "OvTim": clean_value(df.iloc[i, 36]),
                }
            )

            sheet_records += 1

        print(f"{sheet} : {sheet_records} employees extracted")

    # =====================================================
    # Final Dataset
    # =====================================================

    monthly = pd.DataFrame(records)

    if monthly.empty:
        return monthly

    numeric_columns = ["Present", "HL", "WO", "Absent", "Leave", "PaidDays"]

    monthly[numeric_columns] = monthly[numeric_columns].fillna(0)

    monthly = (
        monthly.drop_duplicates(subset=["EmpCode", "Year", "Month"])
        .sort_values(["Department", "EmpCode"])
        .reset_index(drop=True)
    )

    print(f"Total Monthly Records : {len(monthly)}")

    return monthly

# ==========================================================
# MAIN ENTRY POINT
# ==========================================================


def process_report(filepath, save=True):
    """
    Complete ETL Pipeline

    Excel Workbook

        ↓

    Daily Dataset

        ↓

    Monthly Dataset

        ↓

    Save Excel Files

    Returns

        daily

        monthly
    """

    print()

    print("=" * 70)

    print("Attendance Processing Started")

    print("=" * 70)

    print(f"Workbook : {filepath}")

    print()

    # --------------------------------------------------
    # DETECT COMPANY
    # --------------------------------------------------

    company = detect_company(getattr(filepath, "name", str(filepath)))

    if company is None:
        raise ValueError(
            f"Unable to detect company from {getattr(filepath, 'name', filepath)}"
        )

    # --------------------------------------------------
    # DAILY
    # --------------------------------------------------

    print("Extracting Daily Attendance...")

    daily = extract_daily(filepath)

    if not daily.empty:
        daily.insert(0, "Company", company["code"])

    print(f"Daily Records : {len(daily)}")

    print()

    # --------------------------------------------------
    # MONTHLY
    # --------------------------------------------------

    print("Extracting Monthly Attendance...")

    monthly = extract_monthly(filepath)

    if not monthly.empty:
        monthly.insert(0, "Company", company["code"])

    print(f"Monthly Records : {len(monthly)}")

    print()

    # --------------------------------------------------
    # PROCESSING SUMMARY
    # --------------------------------------------------

    summary = {
        "Company": company["code"],
        "Filename": getattr(filepath, "name", Path(filepath).name),
        "Employees": monthly["EmpCode"].nunique(),
        "Departments": monthly["Department"].nunique(),
        "DailyRecords": len(daily),
        "MonthlyRecords": len(monthly),
    }

    return (daily, monthly, summary)


# ==========================================================
# PROCESS MULTIPLE WORKBOOKS
# ==========================================================


def process_reports(file_list):
    """
    Process multiple attendance workbooks.
    """

    if not file_list:
        return (pd.DataFrame(), pd.DataFrame(), [])

    all_daily = []

    all_monthly = []

    all_summary = []

    for file in file_list:
        filename = getattr(file, "name", str(file))

        print(f"\nProcessing workbook: {filename}")

        daily, monthly, summary = process_report(file, save=False)

        if not daily.empty:
            all_daily.append(daily)

        if not monthly.empty:
            all_monthly.append(monthly)

        all_summary.append(summary)

    # ------------------------------------------
    # Merge datasets
    # ------------------------------------------

    daily = pd.concat(all_daily, ignore_index=True) if all_daily else pd.DataFrame()

    monthly = (
        pd.concat(all_monthly, ignore_index=True) if all_monthly else pd.DataFrame()
    )

    # ------------------------------------------
    # Remove duplicates
    # ------------------------------------------

    daily = daily.drop_duplicates(subset=["EmpCode", "Date"])

    monthly = monthly.drop_duplicates(subset=["EmpCode", "Year", "Month"])

    # ------------------------------------------
    # Sort
    # ------------------------------------------

    daily = daily.sort_values(["EmpCode", "Date"]).reset_index(drop=True)

    monthly = monthly.sort_values(
        ["Department", "EmpCode", "Year", "Month"]
    ).reset_index(drop=True)

    # ------------------------------------------
    # Save
    # ------------------------------------------

    if daily.empty or monthly.empty:
        print("Nothing to save.")

        return (daily, monthly, all_summary)

    return daily, monthly, all_summary
