import pandas as pd
from pathlib import Path


# ==========================================================
# FILE VALIDATION
# ==========================================================


def validate_file(filepath):
    """
    Validate an uploaded attendance workbook.

    Checks:
    --------
    1. File exists
    2. Excel extension (.xlsx / .xls)
    3. Workbook can be opened
    4. Workbook contains at least one worksheet

    Returns
    -------
    (True, message)

    or

    (False, message)
    """

    # ------------------------------------------------------
    # Uploaded File Check
    # ------------------------------------------------------

    if filepath is None:
        return (False, "No file selected.")

    # ------------------------------------------------------
    # Extension Check
    # ------------------------------------------------------

    filename = Path(filepath.name).suffix.lower()

    if filename not in [".xlsx", ".xls"]:
        return (False, "Only Excel (.xlsx, .xls) files are supported.")

    # ------------------------------------------------------
    # Workbook Check
    # ------------------------------------------------------

    try:
        xls = pd.ExcelFile(filepath)

    except Exception as e:
        return (False, f"Unable to open workbook.\n\n{e}")

    # ------------------------------------------------------
    # Sheet Check
    # ------------------------------------------------------

    if len(xls.sheet_names) == 0:
        return (False, "Workbook contains no worksheets.")

    # ------------------------------------------------------
    # Empty Sheet Check
    # ------------------------------------------------------

    valid_sheet_count = 0

    for sheet in xls.sheet_names:
        try:
            df = pd.read_excel(filepath, sheet_name=sheet, header=None)

            if not df.empty:
                valid_sheet_count += 1

        except Exception:
            continue

    if valid_sheet_count == 0:
        return (False, "Workbook does not contain any readable worksheets.")

    # ------------------------------------------------------
    # Success
    # ------------------------------------------------------

    return (
        True,
        f"Workbook validated successfully ({valid_sheet_count} sheet(s) detected).",
    )
