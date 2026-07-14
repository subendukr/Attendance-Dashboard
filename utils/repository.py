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

        daily, monthly, summary = (
            process_reports(
                repository,
            )
        )

        logger.info(
            "Repository rebuild completed."
        )

        return (
            daily,
            monthly,
            summary,
        )

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