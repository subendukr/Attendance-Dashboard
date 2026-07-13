from pathlib import Path

import pandas as pd

from utils.repository import AttendanceRepository
from utils.storage import LocalStorage, SupabaseStorage, create_storage, initialize_storage_backend, migrate_local_files_to_storage


def test_repository_uses_storage_root(tmp_path):
    storage = LocalStorage(tmp_path)
    repo = AttendanceRepository(storage=storage)

    repo.ensure_repository()

    assert (tmp_path / "metadata").exists()
    assert (tmp_path / "processed").exists()
    assert (tmp_path / "raw").exists()

    metadata = repo.load_metadata()
    assert metadata.empty
    assert list(metadata.columns) == [
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


def test_repository_can_save_and_load_metadata(tmp_path):
    storage = LocalStorage(tmp_path)
    repo = AttendanceRepository(storage=storage)

    metadata = pd.DataFrame(
        [{"Filename": "sample.xlsx", "Status": "Imported", "FileSizeKB": 12.5}]
    )

    repo.save_metadata(metadata)

    loaded = repo.load_metadata()
    assert loaded.iloc[0]["Filename"] == "sample.xlsx"
    assert loaded.iloc[0]["Status"] == "Imported"


def test_create_storage_uses_environment_configuration(monkeypatch, tmp_path):
    monkeypatch.setenv("ATTENDANCE_STORAGE_BACKEND", "local")
    monkeypatch.setenv("ATTENDANCE_STORAGE_ROOT", str(tmp_path))

    storage = create_storage()

    assert isinstance(storage, LocalStorage)
    assert storage.root == tmp_path


def test_supabase_storage_requires_credentials(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)

    try:
        SupabaseStorage(root=".")
    except ValueError as exc:
        assert "configured" in str(exc)
    else:
        raise AssertionError("SupabaseStorage should require credentials")


def test_migrate_local_files_to_storage(tmp_path):
    source = tmp_path / "data"
    source.mkdir(parents=True)
    test_file = source / "sample.txt"
    test_file.write_text("hello")

    class FakeStorage(LocalStorage):
        pass

    storage = FakeStorage(tmp_path / "target")
    migrated = migrate_local_files_to_storage(storage, source_root=source)

    assert migrated == ["sample.txt"]
    assert (storage.resolve("sample.txt")).exists()


def test_initialize_storage_backend_with_local_backend(tmp_path):
    storage = initialize_storage_backend(backend="local", root=str(tmp_path))
    assert isinstance(storage, LocalStorage)
    assert storage.root == tmp_path
