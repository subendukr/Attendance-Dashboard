import json
import sys
from pathlib import Path

# Ensure project root is on sys.path so `utils` package is importable
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

try:
    from utils.repository import repo
except Exception as e:
    print(json.dumps({"error": f"failed_import_repo: {e}"}))
    sys.exit(1)

storage = repo.storage
info = {
    "storage_class": storage.__class__.__name__,
    "storage_root": getattr(storage, 'root', None),
    "storage_bucket": getattr(storage, 'bucket', None) if hasattr(storage, 'bucket') else None,
}

try:
    files = repo.list_repository()
    files = [str(p) for p in files]
except Exception as e:
    files = f"error: {e}"

print(json.dumps({"info": info, "files": files}, default=str))