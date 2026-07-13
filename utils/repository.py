import pandas as pd
from datetime import datetime
from pathlib import Path
import shutil

from utils.parser import process_reports
from utils.company_detector import detect_company
from utils.storage import LocalStorage, create_storage


class AttendanceRepository:
    """Central gateway for repository storage and metadata access."""

    def __init__(self, storage=None):
        # Default storage root should be the repository 'data' folder
        self.storage = storage or create_storage(root=Path("data"))
        self.raw_folder = "raw"
        self.processed_folder = "processed"
        self.metadata_folder = "metadata"
        self.metadata_file = self.storage.resolve(self.metadata_folder, "upload_history.csv")

    def ensure_repository(self):
        """Create all repository folders and metadata storage."""
        self.storage.ensure_directory(self.raw_folder)
        self.storage.ensure_directory(self.processed_folder)
        self.storage.ensure_directory(self.metadata_folder)
        self.ensure_metadata()

    def ensure_metadata(self):
        """Create upload_history.csv if it does not exist."""
        if self.storage.exists("metadata/upload_history.csv"):
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
        self.save_metadata(metadata)

    def load_metadata(self):
        """Load upload history."""
        self.ensure_metadata()
        return pd.read_csv(self.metadata_file)

    def save_metadata(self, metadata):
        """Save upload history."""
        self.storage.ensure_directory(self.metadata_folder)
        metadata.to_csv(self.metadata_file, index=False)

    def add_metadata(self, filename, filesize_kb, status):
        """Add a workbook entry to upload history."""
        metadata = self.load_metadata()

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
        self.save_metadata(metadata)

    def list_repository(self):
        """Return all workbooks stored in the raw repository."""
        self.ensure_repository()
        files = self.storage.list_files(self.raw_folder, pattern="*.xlsx")

        resolved = []

        for path in files:
            # storage.list_files may return Path objects or lightweight items
            # Normalize to a fully resolved path under the storage root/raw
            name = path.name if hasattr(path, "name") else str(path)

            resolved.append(self.storage.resolve(self.raw_folder, name))

        return sorted(resolved)

    def workbook_exists(self, filename):
        """Check whether a workbook already exists in the raw repository."""
        self.ensure_repository()
        return self.storage.exists(f"{self.raw_folder}/{filename}")

    def save_raw_workbook(self, uploaded_file):
        """Save an uploaded workbook into the raw repository."""
        self.ensure_repository()
        destination = self.storage.write_bytes(f"{self.raw_folder}/{uploaded_file.name}", uploaded_file.getbuffer())
        return destination

    def delete_workbook(self, filename):
        """Delete a workbook from the repository."""
        path = f"{self.raw_folder}/{filename}"
        if not self.storage.exists(path):
            return False, "Workbook does not exist."

        try:
            self.storage.delete(path)
            return True, "Workbook deleted successfully."
        except PermissionError:
            return False, "Permission denied. Could not delete workbook."
        except Exception as e:
            return False, str(e)

    def clear_repository(self):
        """Remove every workbook stored in the repository."""
        self.ensure_repository()
        for workbook in self.storage.list_files(self.raw_folder, pattern="*.xlsx"):
            self.storage.delete(f"{self.raw_folder}/{workbook.name}")

    def copy_workbook(self, source):
        """Copy an existing workbook into the repository."""
        self.ensure_repository()
        destination = self.storage.resolve(self.raw_folder, Path(source).name)
        shutil.copy2(source, destination)
        return destination

    def update_metadata(self, filename, employees, departments, daily_records, monthly_records, month=None, year=None):
        """Update processing statistics for an existing workbook."""
        metadata = self.load_metadata()
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
        self.save_metadata(metadata)

    def remove_metadata(self, filename):
        """Remove a workbook from upload_history.csv."""
        metadata = self.load_metadata()
        metadata = metadata[metadata["Filename"] != filename]
        self.save_metadata(metadata)
        return True

    def rebuild_repository(self):
        """Rebuild processed datasets from all raw workbooks."""
        repository = self.list_repository()
        if not repository:
            return None, None, []
        daily, monthly, summary = process_reports(repository)
        return daily, monthly, summary


# Backward-compatible singleton instance for the existing app
repo = AttendanceRepository()


def ensure_repository():
    return repo.ensure_repository()


def load_metadata():
    return repo.load_metadata()


def save_metadata(metadata):
    return repo.save_metadata(metadata)


def add_metadata(filename, filesize_kb, status):
    return repo.add_metadata(filename, filesize_kb, status)


def list_repository():
    return repo.list_repository()


def workbook_exists(filename):
    return repo.workbook_exists(filename)


def save_raw_workbook(uploaded_file):
    return repo.save_raw_workbook(uploaded_file)


def delete_workbook(filename):
    return repo.delete_workbook(filename)


def clear_repository():
    return repo.clear_repository()


def copy_workbook(source):
    return repo.copy_workbook(source)


def update_metadata(filename, employees, departments, daily_records, monthly_records, month=None, year=None):
    return repo.update_metadata(filename, employees, departments, daily_records, monthly_records, month=month, year=year)


def remove_metadata(filename):
    return repo.remove_metadata(filename)


def rebuild_repository():
    return repo.rebuild_repository()
