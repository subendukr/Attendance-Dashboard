"""
Repository layer for the Attendance Dashboard.

The repository is responsible for managing attendance workbooks,
metadata, and processed datasets while remaining completely
independent of the underlying storage backend.

All file operations are delegated to StorageAdapter.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import pandas as pd

from utils.company_detector import detect_company
from utils.parser import process_reports
from utils.storage import StorageAdapter, create_storage


logger = logging.getLogger(__name__)


class AttendanceRepository:
    """
    Central gateway for attendance repository operations.

    This class never communicates directly with the filesystem.
    Every file operation goes through StorageAdapter, allowing the
    application to switch between LocalStorage, SupabaseStorage,
    or any future backend without modifying repository logic.
    """

    # ------------------------------------------------------------------
    # Repository folders
    # ------------------------------------------------------------------

    RAW_FOLDER = "raw"
    PROCESSED_FOLDER = "processed"
    METADATA_FOLDER = "metadata"

    USERS_FILE = "users.csv"
    ROLES_FILE = "roles.json"
    COMPANIES_FILE = "companies.json"

    METADATA_FILE = "metadata/upload_history.csv"

    # ------------------------------------------------------------------
    # Metadata schema
    # ------------------------------------------------------------------

    METADATA_COLUMNS = [
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

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        storage: Optional[StorageAdapter] = None,
    ) -> None:
        """
        Create a repository instance.

        Parameters
        ----------
        storage
            Optional storage backend.

            If omitted, the configured backend from the environment
            will be created automatically.
        """

        self.storage = storage or create_storage(root="data")

        logger.info(
            "AttendanceRepository initialized using %s",
            self.storage.__class__.__name__,
        )

        self.ensure_repository()

    # ------------------------------------------------------------------
    # Repository initialization
    # ------------------------------------------------------------------

    def ensure_repository(self) -> None:
        """
        Ensure that all repository folders and metadata exist.
        """

        logger.debug("Ensuring repository structure.")

        self.storage.ensure_directory(
            self.RAW_FOLDER,
        )

        self.storage.ensure_directory(
            self.PROCESSED_FOLDER,
        )

        self.storage.ensure_directory(
            self.METADATA_FOLDER,
        )

        self.ensure_metadata()

    # ------------------------------------------------------------------
    # Metadata initialization
    # ------------------------------------------------------------------

    def ensure_metadata(self) -> None:
        """
        Create upload_history.csv if it does not already exist.
        """

        if self.storage.exists(
            self.METADATA_FILE,
        ):
            return

        logger.info(
            "Creating repository metadata."
        )

        metadata = pd.DataFrame(
            columns=self.METADATA_COLUMNS,
        )

        self.storage.save_csv(
            metadata,
            self.METADATA_FILE,
        )

    # ------------------------------------------------------------------
    # User management
    # ------------------------------------------------------------------

    def load_users(self) -> pd.DataFrame:
        """
        Load repository user data.
        """

        if not self.storage.exists(self.USERS_FILE):
            logger.debug("Users file not found: %s", self.USERS_FILE)
            return pd.DataFrame(
                columns=[
                    "Username",
                    "Password",
                    "Role",
                    "Name",
                    "Active",
                ]
            )

        logger.debug("Loading repository users.")

        users = self.storage.load_csv(self.USERS_FILE)

        if "Active" in users.columns:
            users["Active"] = (
                users["Active"]
                .astype(str)
                .str.upper()
                .eq("TRUE")
            )

        return users

    def save_users(
            self,
            users: pd.DataFrame
        ) -> str:
        """
        Persist repository user data.
        """

        logger.debug(
            "Saving repository users (%d rows).",
            len(users),
        )

        return self.storage.save_csv(
            users,
            self.USERS_FILE,
        )
    
    # ------------------------------------------------------------------
    # Role management
    # ------------------------------------------------------------------

    def load_roles(self)-> dict:
        """
        Load repository role definitions.

        Returns
        -------
        dict
            Dictionary containing all role definitions.
        """

        if not self.storage.exists(self.ROLES_FILE):

            logger.debug(
                "Roles file not found: %s",
                self.ROLES_FILE,
            )

            return {}

        logger.debug(
            "Loading repository roles."
        )

        return self.storage.load_json(
            self.ROLES_FILE,
        )

    def save_roles(
        self,
        roles: dict,
    ):
        """
        Persist repository role definitions.

        Parameters
        ----------
        roles
            Dictionary containing all role definitions.

        Returns
        -------
        str
            Storage location of the saved JSON file.
        """

        logger.debug(
            "Saving repository roles."
        )

        return self.storage.save_json(
            roles,
            self.ROLES_FILE,
        )

    # ------------------------------------------------------------------
    # Company Management
    # ------------------------------------------------------------------
    def load_companies(self) -> dict:
        """
        Load repository company configuration.

        Returns
        -------
        dict
            Dictionary containing the complete company configuration.
        """

        if not self.storage.exists(self.COMPANIES_FILE):

            logger.debug(
                "Companies file not found: %s",
                self.COMPANIES_FILE,
            )

            return {}

        logger.debug(
            "Loading repository companies."
        )

        return self.storage.load_json(
            self.COMPANIES_FILE,
        )


    def save_companies(
        self,
        companies: dict,
    ):
        """
        Persist repository company configuration.

        Parameters
        ----------
        companies
            Complete company configuration dictionary.

        Returns
        -------
        str
            Storage location of the saved JSON file.
        """

        logger.debug(
            "Saving repository companies (%d companies).",
            len(companies.get("companies", {})),
        )

        return self.storage.save_json(
            companies,
            self.COMPANIES_FILE,
        )
    # ------------------------------------------------------------------
    # Metadata operations
    # ------------------------------------------------------------------

    def load_metadata(self) -> pd.DataFrame:
        """
        Load repository metadata.

        Returns
        -------
        pandas.DataFrame
            Upload history for all workbooks.
        """

        self.ensure_metadata()

        logger.debug(
            "Loading repository metadata."
        )

        return self.storage.load_csv(
            self.METADATA_FILE,
        )

    def save_metadata(
        self,
        metadata: pd.DataFrame,
    ) -> None:
        """
        Persist repository metadata.

        Parameters
        ----------
        metadata
            Upload history dataframe.
        """

        logger.debug(
            "Saving repository metadata (%d rows).",
            len(metadata),
        )

        self.storage.save_csv(
            metadata,
            self.METADATA_FILE,
        )

    def add_metadata(
        self,
        filename: str,
        filesize_kb: float,
        status: str,
    ) -> None:
        """
        Add a workbook entry into upload history.
        """

        metadata = self.load_metadata()

        if filename in metadata["Filename"].values:
            logger.debug(
                "Metadata already exists for %s",
                filename,
            )
            return

        company = detect_company(filename)

        company_name = (
            company["name"]
            if company
            else "Unknown"
        )

        company_code = (
            company["code"]
            if company
            else ""
        )

        new_row = {
            "Company": company_name,
            "CompanyCode": company_code,
            "Filename": filename,
            "UploadedOn": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Month": "",
            "Year": "",
            "FileSizeKB": round(filesize_kb, 2),
            "Status": status,
            "Employees": "",
            "Departments": "",
            "DailyRecords": "",
            "MonthlyRecords": "",
        }

        metadata.loc[
            len(metadata)
        ] = new_row

        self.save_metadata(
            metadata,
        )

        logger.info(
            "Metadata added for %s",
            filename,
        )

    def update_metadata(
        self,
        filename: str,
        employees: int,
        departments: int,
        daily_records: int,
        monthly_records: int,
        month=None,
        year=None,
    ) -> None:
        """
        Update processing statistics for a workbook.
        """

        metadata = self.load_metadata()

        matches = metadata.index[
            metadata["Filename"] == filename
        ]

        if len(matches) == 0:

            logger.warning(
                "No metadata found for %s",
                filename,
            )

            return

        idx = matches[0]

        metadata.loc[idx, "Employees"] = employees
        metadata.loc[idx, "Departments"] = departments
        metadata.loc[idx, "DailyRecords"] = daily_records
        metadata.loc[idx, "MonthlyRecords"] = monthly_records

        if month is not None:
            metadata.loc[idx, "Month"] = month

        if year is not None:
            metadata.loc[idx, "Year"] = year

        self.save_metadata(
            metadata,
        )

        logger.info(
            "Metadata updated for %s",
            filename,
        )

    def remove_metadata(
        self,
        filename: str,
    ) -> bool:
        """
        Remove a workbook from upload history.
        """

        metadata = self.load_metadata()

        original_rows = len(metadata)

        metadata = metadata[
            metadata["Filename"] != filename
        ]

        if len(metadata) == original_rows:

            logger.warning(
                "Metadata not found for %s",
                filename,
            )

            return False

        self.save_metadata(
            metadata,
        )

        logger.info(
            "Metadata removed for %s",
            filename,
        )

        return True

    # ------------------------------------------------------------------
    # Repository operations
    # ------------------------------------------------------------------

    def list_repository(self) -> list:
        """
        Return every workbook stored in the raw repository.

        Returns
        -------
        list
            List of storage-resolved workbook locations.
        """

        self.ensure_repository()

        files = self.storage.list_files(
            self.RAW_FOLDER,
            pattern="*.xlsx",
        )

        repository = []

        for item in files:

            name = (
                item.name
                if hasattr(item, "name")
                else str(item)
            )

            repository.append(
                self.storage.resolve(
                    self.RAW_FOLDER,
                    name,
                )
            )

        repository.sort()

        logger.debug(
            "Repository contains %d workbook(s).",
            len(repository),
        )

        return repository

    def workbook_exists(
        self,
        filename: str,
    ) -> bool:
        """
        Check whether a workbook already exists.
        """

        return self.storage.exists(
            f"{self.RAW_FOLDER}/{filename}"
        )

    def save_raw_workbook(self,uploaded_file,):
        """
        Store an uploaded workbook in the repository.
        """

        destination = (f"{self.RAW_FOLDER}/"f"{uploaded_file.name}")

        logger.info("Saving workbook %s",uploaded_file.name)

        self.storage.write_bytes(destination,uploaded_file.getvalue())

        return self.storage.resolve(destination)

    def save_processed_data(self,daily,monthly):

        logger.info(
            "Daily rows: %d | Monthly rows: %d",
            len(daily),
            len(monthly),
        )

        self.storage.save_dataframe(
            daily,
            f"{self.PROCESSED_FOLDER}/EmployeeDaily.xlsx",
        )

        logger.info("EmployeeDaily.xlsx saved")

        self.storage.save_dataframe(
            monthly,
            f"{self.PROCESSED_FOLDER}/EmployeeMonthly.xlsx",
        )

        logger.info("EmployeeMonthly.xlsx saved")

    def processed_exists(self) -> bool:
        """
        Check whether the processed attendance datasets exist.

        The repository defines what constitutes a "processed repository".
        Currently, both EmployeeDaily.xlsx and EmployeeMonthly.xlsx
        must exist.

        Returns
        -------
        bool
            True if both processed datasets exist.
        """

        return (
            self.storage.exists(
                f"{self.PROCESSED_FOLDER}/EmployeeDaily.xlsx"
            )
            and
            self.storage.exists(
                f"{self.PROCESSED_FOLDER}/EmployeeMonthly.xlsx"
            )
        )

    def load_daily(self) -> pd.DataFrame:
        """
        Load the processed daily attendance dataset.

        Returns
        -------
        pandas.DataFrame
            Daily attendance dataset with normalized columns.

        Raises
        ------
        FileNotFoundError
            If the processed dataset does not exist.
        """

        relative_path = (
            f"{self.PROCESSED_FOLDER}/EmployeeDaily.xlsx"
        )

        if not self.storage.exists(relative_path):

            raise FileNotFoundError(
                "Processed daily dataset not found.\n\n"
                "Please upload and process an attendance report first."
            )

        logger.debug(
            "Loading processed daily dataset."
        )

        dataframe = self.storage.load_dataframe(
            relative_path,
        )

        # --------------------------------------------------
        # Normalization
        # --------------------------------------------------

        if (
            "Date" in dataframe.columns
            and not pd.api.types.is_datetime64_any_dtype(
                dataframe["Date"]
            )
        ):
            dataframe["Date"] = pd.to_datetime(
                dataframe["Date"],
                errors="coerce",
            )

        return dataframe

    def load_monthly(self) -> pd.DataFrame:
        """
        Load the processed monthly attendance dataset.

        Returns
        -------
        pandas.DataFrame
            Monthly attendance dataset.

        Raises
        ------
        FileNotFoundError
            If the processed dataset does not exist.
        """

        relative_path = (
            f"{self.PROCESSED_FOLDER}/EmployeeMonthly.xlsx"
        )

        if not self.storage.exists(relative_path):

            raise FileNotFoundError(
                "Processed monthly dataset not found.\n\n"
                "Please upload and process an attendance report first."
            )

        logger.debug(
            "Loading processed monthly dataset."
        )

        dataframe = self.storage.load_dataframe(
            relative_path,
        )

        # --------------------------------------------------
        # Future normalization can be added here
        # --------------------------------------------------

        return dataframe
    
    def processed_last_updated(self):
        """
        Return the last modified timestamp of the processed datasets.

        Returns
        -------
        datetime | None
            Last modified time of the processed repository,
            or None if no processed data exists.
        """

        if not self.processed_exists():
            return None

        file_path = self.storage.resolve(
            f"{self.PROCESSED_FOLDER}/EmployeeMonthly.xlsx"
        )

        return datetime.fromtimestamp(
            file_path.stat().st_mtime
        )

    def copy_workbook(self,source):
        """
        Copy an existing workbook into the repository.

        Unlike the previous implementation,
        this version works with every storage backend.
        """

        source = self.storage.resolve(source)

        destination = (
            f"{self.RAW_FOLDER}/"
            f"{source.name}"
        )

        logger.info(
            "Copying workbook %s",
            source.name,
        )

        with open(
            source,
            "rb",
        ) as handle:

            self.storage.write_bytes(
                destination,
                handle.read(),
            )

        return self.storage.resolve(
            destination,
        )

    def delete_workbook(
        self,
        filename: str,
    ):
        """
        Delete a workbook from the repository.
        """

        relative_path = (
            f"{self.RAW_FOLDER}/{filename}"
        )

        if not self.storage.exists(
            relative_path,
        ):

            logger.warning(
                "Workbook not found: %s",
                filename,
            )

            return (
                False,
                "Workbook does not exist.",
            )

        try:

            self.storage.delete(
                relative_path,
            )

            logger.info(
                "Deleted workbook %s",
                filename,
            )

            return (
                True,
                "Workbook deleted successfully.",
            )

        except Exception as exc:

            logger.exception(
                "Unable to delete workbook %s",
                filename,
            )

            return (
                False,
                str(exc),
            )

    def clear_repository(self) -> None:
        """
        Remove every workbook from the repository.
        """

        files = self.storage.list_files(
            self.RAW_FOLDER,
            pattern="*.xlsx",
        )

        removed = 0

        for workbook in files:

            name = (
                workbook.name
                if hasattr(workbook, "name")
                else str(workbook)
            )

            self.storage.delete(
                f"{self.RAW_FOLDER}/{name}"
            )

            removed += 1

        logger.info(
            "Repository cleared (%d workbook(s)).",
            removed,
        )

    def rebuild_repository(self):
        """
        Rebuild processed datasets from every
        workbook currently stored.
        """

        repository = self.list_repository()

        if not repository:

            logger.warning(
                "Repository is empty."
            )

            return (
                None,
                None,
                [],
            )

        logger.info(
            "Processing %d workbook(s).",
            len(repository),
        )

        daily, monthly, summary = process_reports(repository)

        self.save_processed_data(daily,monthly)

        logger.info(
            "Repository rebuild completed."
        )

        return daily, monthly, summary


# ==============================================================================
# Singleton Repository
# ==============================================================================

logger.info(
    "Creating repository singleton."
)

repo = AttendanceRepository()


# ==============================================================================
# Backward-compatible wrapper functions
# ==============================================================================

def ensure_repository():
    """
    Ensure the repository structure exists.
    """
    return repo.ensure_repository()


def load_metadata():
    """
    Load upload history.
    """
    return repo.load_metadata()


def save_metadata(
    metadata: pd.DataFrame,
):
    """
    Save upload history.
    """
    return repo.save_metadata(metadata)


def add_metadata(
    filename,
    filesize_kb,
    status,
):
    """
    Register a workbook upload.
    """
    return repo.add_metadata(
        filename,
        filesize_kb,
        status,
    )


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
    Update workbook statistics.
    """
    return repo.update_metadata(
        filename,
        employees,
        departments,
        daily_records,
        monthly_records,
        month=month,
        year=year,
    )


def remove_metadata(
    filename,
):
    """
    Remove workbook metadata.
    """
    return repo.remove_metadata(
        filename,
    )


def list_repository():
    """
    Return every workbook stored in the repository.
    """
    return repo.list_repository()


def workbook_exists(
    filename,
):
    """
    Check whether a workbook exists.
    """
    return repo.workbook_exists(
        filename,
    )


def save_raw_workbook(
    uploaded_file,
):
    """
    Store an uploaded workbook.
    """
    return repo.save_raw_workbook(
        uploaded_file,
    )


def copy_workbook(
    source,
):
    """
    Copy an existing workbook into the repository.
    """
    return repo.copy_workbook(
        source,
    )


def delete_workbook(
    filename,
):
    """
    Delete a workbook.
    """
    return repo.delete_workbook(
        filename,
    )


def clear_repository():
    """
    Remove every workbook from the repository.
    """
    return repo.clear_repository()


def rebuild_repository():
    """
    Rebuild processed datasets.
    """
    return repo.rebuild_repository()


def processed_exists():
    """
    Check whether processed datasets exist.
    """
    return repo.processed_exists()


def load_daily():
    """
    Load processed daily attendance data.
    """
    return repo.load_daily()


def load_monthly():
    """
    Load processed monthly attendance data.
    """
    return repo.load_monthly()

def processed_last_updated():
    """
    Return the last updated timestamp
    of the processed repository.
    """
    return repo.processed_last_updated()


def load_users():
    """
    Load repository users data.
    """
    return repo.load_users()

def load_roles():
    return repo.load_roles()

def save_roles(roles):
    return repo.save_roles(roles)

def load_companies():
    """
    Load repository company configuration.
    """
    return repo.load_companies()


def save_companies(companies):
    """
    Save repository company configuration.
    """
    return repo.save_companies(companies)

def save_users(users):
    """
    Save repository users data.
    """
    return repo.save_users(users)