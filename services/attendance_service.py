import logging

from utils.data_access import (
    load_daily_data,
    load_monthly_data,
)

from utils.repository import (
    ensure_repository,
    processed_exists,
)

from utils.repository import (
    processed_last_updated,
)


logger = logging.getLogger(__name__)


class AttendanceService:
    """
    Service layer responsible for providing attendance
    datasets to the UI.

    Repository exceptions are translated into application-
    friendly responses.
    """

    def get_daily_data(self):
        try:
            return load_daily_data()

        except FileNotFoundError:

            logger.info(
                "Processed daily dataset not available."
            )

            return None

    def get_monthly_data(self):
        try:
            return load_monthly_data()

        except FileNotFoundError:

            logger.info(
                "Processed monthly dataset not available."
            )

            return None

    def has_processed_data(self):
        """
        Returns True if the processed attendance repository exists.
        """
        return processed_exists()
    
    def ensure_ready(self):
        """
        Ensure the attendance repository is initialized.

        Creates the required repository folders and metadata
        if they do not already exist.
        """
        ensure_repository()

    def get_processed_last_updated(self):
        """
        Return the timestamp of the latest
        processed attendance dataset.
        """
        return processed_last_updated()

attendance_service = AttendanceService()