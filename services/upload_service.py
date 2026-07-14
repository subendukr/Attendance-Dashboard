from utils.parser import process_reports
from utils.repository import repo


class UploadService:
    """Service for orchestrating upload, processing, and repository rebuilds."""

    def __init__(self, repository=None):
        self.repository = repository or repo

    def process_workbooks(self, files):
        return process_reports(files)

    def rebuild_repository(self):
        return self.repository.rebuild_repository()


upload_service = UploadService()
