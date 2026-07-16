import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.storage import ( # noqa: E402 
    initialize_storage_backend, 
    migrate_local_files_to_storage,
)

def main():
    backend = os.getenv("ATTENDANCE_STORAGE_BACKEND", "supabase")
    root = os.getenv("ATTENDANCE_STORAGE_ROOT", "data")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    bucket = os.getenv("SUPABASE_BUCKET", "attendance")

    storage = initialize_storage_backend(backend=backend, root=root, url=url, key=key, bucket=bucket)
    migrated = migrate_local_files_to_storage(storage, source_root=Path("data"))

    print(f"Migrated {len(migrated)} files to {backend} storage")
    for item in migrated[:10]:
        print(f"- {item}")


if __name__ == "__main__":
    main()
