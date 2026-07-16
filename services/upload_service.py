from utils.parser import process_reports
from utils.repository import repo
import logging

logger = logging.getLogger(__name__)


class UploadService:
    """Service for orchestrating upload, processing, and repository rebuilds."""

    def __init__(self, repository=None):
        self.repository = repository or repo

    def process_workbooks(self, files):

        try:
            daily, monthly, summary = process_reports(files)

            self.repository.save_processed_data(daily, monthly)

            return daily, monthly, summary

        except Exception:
            logger.exception("Failed to process uploaded workbooks.")
            raise

    def rebuild_repository(self):
        return self.repository.rebuild_repository()


upload_service = UploadService()
