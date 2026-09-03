from utils.parser import process_reports
from utils.repository import repo
from utils.cache import clear_cache
import logging

logger = logging.getLogger(__name__)


class UploadService:
    """Service for orchestrating upload, processing, and repository rebuilds."""

    def __init__(self, repository=None):
        self.repository = repository or repo

    def process_workbooks(self, files):

        try:
            daily, monthly, summary = process_reports(files)

            self.repository.append_processed_data(daily, monthly)

            clear_cache()

            return daily, monthly, summary

        except Exception:
            logger.exception("Failed to process uploaded workbooks.")
            raise

    def rebuild_repository(self):
        try:
            result = self.repository.rebuild_repository()

            clear_cache()

            return result
        
        except Exception:
            logger.exception("Failed to rebuild repository.")
            raise

upload_service = UploadService()
