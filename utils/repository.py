import pandas as pd
from datetime import datetime
from pathlib import Path
import shutil
from utils.parser import process_reports
from utils.company_detector import detect_company

# ==========================================================
# Repository Paths
# ==========================================================

RAW_FOLDER = Path("data/raw")

PROCESSED_FOLDER = Path("data/processed")

# ==========================================================
# Metadata Paths
# ==========================================================

METADATA_FOLDER = Path("data/metadata")

METADATA_FILE = METADATA_FOLDER / "upload_history.csv"

# ==========================================================
# Repository Initialization
# ==========================================================


def ensure_repository():
    """
    Create all repository folders and metadata storage.
    """

    RAW_FOLDER.mkdir(parents=True, exist_ok=True)

    PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

    METADATA_FOLDER.mkdir(parents=True, exist_ok=True)

    ensure_metadata()


# ==========================================================
# Load Metadata
# ==========================================================


def load_metadata():
    """
    Load upload history.
    """

    ensure_metadata()

    return pd.read_csv(METADATA_FILE)


# ==========================================================
# Save Metadata
# ==========================================================


def save_metadata(metadata):
    """
    Save upload history.
    """

    metadata.to_csv(METADATA_FILE, index=False)


# ==========================================================
# Add Upload Record
# ==========================================================


def add_metadata(
    filename,
    filesize_kb,
    status,
):
    """
    Add a workbook entry to upload history.
    """

    metadata = load_metadata()

    # ==========================================================
    # DETECT COMPANY
    # ==========================================================

    company = detect_company(filename)

    if company:
        company_name = company["name"]

        company_code = company["code"]

    else:
        company_name = "Unknown"

        company_code = ""

    new_row = {
        "Filename": filename,
        "UploadedOn": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "FileSizeKB": round(filesize_kb, 2),
        "Status": status,
        "Company": company_name,
        "CompanyCode": company_code,
        "Month": "",
        "Year": "",
        "Employees": "",
        "Departments": "",
        "DailyRecords": "",
        "MonthlyRecords": "",
    }

    if filename in metadata["Filename"].values:
        return

    metadata.loc[len(metadata)] = new_row

    save_metadata(metadata)


# ==========================================================
# Metadata Initialization
# ==========================================================


def ensure_metadata():
    """
    Create upload_history.csv if it does not exist.
    """

    if METADATA_FILE.exists():
        return

    columns = [
        "Company",
        "CompanyCode",
        "Filename",
        "UploadedOn",
        "Month",
        "Year",
        "FileSizeKB",
        "Status",
        "Employees",
        "Departments",
        "DailyRecords",
        "MonthlyRecords",
    ]

    metadata = pd.DataFrame(columns=columns)

    metadata.to_csv(METADATA_FILE, index=False)


# ==========================================================
# List Repository
# ==========================================================


def list_repository():
    """
    Return all workbooks stored in the raw repository.
    """

    ensure_repository()

    return sorted(RAW_FOLDER.glob("*.xlsx"))


# ==========================================================
# Check Duplicate Workbook
# ==========================================================


def workbook_exists(filename):
    """
    Check whether a workbook already exists
    in the raw repository.
    """

    ensure_repository()

    return (RAW_FOLDER / filename).exists()


# ==========================================================
# Save Workbook
# ==========================================================


def save_raw_workbook(uploaded_file):
    """
    Save an uploaded workbook into data/raw.

    Returns
    -------
    Path
        Saved workbook path.
    """

    ensure_repository()

    destination = RAW_FOLDER / uploaded_file.name

    with open(destination, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return destination


# ==========================================================
# Delete Workbook
# ==========================================================


def delete_workbook(filename):
    """
    Delete a workbook from the repository.
    """

    path = RAW_FOLDER / filename

    if not path.exists():
        return False, "Workbook does not exist."

    try:
        path.unlink()

        return True, "Workbook deleted successfully."

    except PermissionError:
        return False, "Permission denied. Could not delete workbook."

    except Exception as e:
        return False, str(e)


# ==========================================================
# Clear Repository
# ==========================================================


def clear_repository():
    """
    Remove every workbook stored in the repository.
    """

    ensure_repository()

    for workbook in RAW_FOLDER.glob("*.xlsx"):
        workbook.unlink()


# ==========================================================
# Copy Existing Workbook
# ==========================================================


def copy_workbook(source):
    """
    Copy an existing workbook into the repository.

    Useful for testing or rebuilding.
    """

    ensure_repository()

    destination = RAW_FOLDER / Path(source).name

    shutil.copy2(source, destination)

    return destination


# ==========================================================
# Update Processing Metadata
# ==========================================================


def update_metadata(
    filename,
    employees,
    departments,
    daily_records,
    monthly_records,
    month=None,
    year=None,
):
    """
    Update processing statistics for an existing workbook.
    """

    metadata = load_metadata()

    index = metadata.index[metadata["Filename"] == filename]

    if len(index) == 0:
        return

    idx = index[0]

    metadata.loc[idx, "Employees"] = employees
    metadata.loc[idx, "Departments"] = departments
    metadata.loc[idx, "DailyRecords"] = daily_records
    metadata.loc[idx, "MonthlyRecords"] = monthly_records
    if month is not None:
        metadata.loc[idx, "Month"] = month
    if year is not None:
        metadata.loc[idx, "Year"] = year

    save_metadata(metadata)


# ==========================================================
# REMOVE METADATA
# ==========================================================


def remove_metadata(filename):
    """
    Remove a workbook from upload_history.csv
    """

    metadata = load_metadata()

    metadata = metadata[metadata["Filename"] != filename]

    save_metadata(metadata)

    return True


# ==========================================================
# REBUILD REPOSITORY
# ==========================================================


def rebuild_repository():
    """
    Rebuild processed datasets from
    all raw workbooks.
    """

    repository = list_repository()

    if not repository:
        return None, None, []

    daily, monthly, summary = process_reports(repository)

    return daily, monthly, summary
