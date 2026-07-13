from utils.data_access import load_daily_data, load_monthly_data
from utils.repository import repo


class AttendanceService:
    """Business-facing service for loading attendance datasets."""

    def __init__(self, repository=None):
        self.repository = repository or repo

    def get_monthly_data(self):
        return load_monthly_data()

    def get_daily_data(self):
        return load_daily_data()

    def get_repository_files(self):
        return self.repository.list_repository()

    def ensure_ready(self):
        self.repository.ensure_repository()
        return True


attendance_service = AttendanceService()
