"""
Compatibility wrapper around AttendanceRepository.

The rest of the application should obtain processed datasets
through the repository rather than interacting with the
StorageAdapter directly.
"""

from utils.repository import (
    load_daily as repository_load_daily,
    load_monthly as repository_load_monthly,
)


def load_daily():
    """
    Load processed daily attendance data.
    """
    return repository_load_daily()


def load_monthly():
    """
    Load processed monthly attendance data.
    """
    return repository_load_monthly()