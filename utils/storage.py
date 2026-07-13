import os
import tempfile
from pathlib import Path
from typing import Optional

import pandas as pd

try:
    from supabase import create_client
except ImportError:
    create_client = None


class StorageAdapter:
    """Simple storage abstraction for repository-backed data access."""

    def ensure_directory(self, *parts):
        raise NotImplementedError

    def resolve(self, *parts):
        raise NotImplementedError

    def list_files(self, relative_dir=".", pattern="*"):
        raise NotImplementedError

    def write_bytes(self, relative_path, content):
        raise NotImplementedError

    def read_bytes(self, relative_path):
        raise NotImplementedError

    def delete(self, relative_path):
        raise NotImplementedError

    def exists(self, relative_path):
        raise NotImplementedError

    def save_dataframe(self, dataframe: pd.DataFrame, relative_path):
        raise NotImplementedError

    def load_dataframe(self, relative_path):
        raise NotImplementedError


class LocalStorage(StorageAdapter):
    def __init__(self, root=None):
        self.root = Path(root) if root is not None else Path.cwd()

    def ensure_directory(self, *parts):
        path = self.resolve(*parts)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def resolve(self, *parts):
        return self.root.joinpath(*parts)

    def list_files(self, relative_dir=".", pattern="*"):
        directory = self.resolve(relative_dir)
        if not directory.exists():
            return []
        return sorted([path for path in directory.glob(pattern) if path.is_file()])

    def write_bytes(self, relative_path, content):
        path = self.resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def read_bytes(self, relative_path):
        path = self.resolve(relative_path)
        return path.read_bytes()

    def delete(self, relative_path):
        path = self.resolve(relative_path)
        if not path.exists():
            return False
        path.unlink()
        return True

    def exists(self, relative_path):
        return self.resolve(relative_path).exists()

    def save_dataframe(self, dataframe: pd.DataFrame, relative_path):
        path = self.resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        dataframe.to_excel(path, index=False)
        return path

    def load_dataframe(self, relative_path):
        path = self.resolve(relative_path)
        if not path.exists():
            raise FileNotFoundError(path)
        return pd.read_excel(path)


class SupabaseStorage(StorageAdapter):
    """Supabase-backed storage adapter for attendance datasets and metadata."""

    def __init__(self, root=None, url=None, key=None, bucket=None):
        self.root = Path(root) if root is not None else Path.cwd()
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        self.bucket = bucket or os.getenv("SUPABASE_BUCKET") or "attendance"
        self._client = None

        if not self.url or not self.key:
            raise ValueError("Supabase credentials are not configured")

        if create_client is None:
            raise ImportError("The 'supabase' package is required for SupabaseStorage")

        self._client = create_client(self.url, self.key)

    @property
    def client(self):
        if self._client is None:
            self._client = create_client(self.url, self.key)
        return self._client

    def ensure_directory(self, *parts):
        return self.resolve(*parts)

    def resolve(self, *parts):
        return self.root.joinpath(*parts)

    def _path_to_key(self, relative_path):
        return str(Path(relative_path).as_posix())

    def list_files(self, relative_dir=".", pattern="*"):
        try:
            response = self.client.storage.from_(self.bucket).list(path=self._path_to_key(relative_dir))
            items = response if isinstance(response, list) else []
            return [Path(item.get("name", "")) for item in items if item.get("name")]
        except Exception:
            return []

    def write_bytes(self, relative_path, content):
        key = self._path_to_key(relative_path)
        try:
            self.client.storage.from_(self.bucket).upload(file=content, path=key)
        except Exception as exc:
            raise RuntimeError(f"Failed to upload '{key}' to bucket '{self.bucket}'.") from exc
        return self.resolve(relative_path)

    def read_bytes(self, relative_path):
        key = self._path_to_key(relative_path)
        try:
            response = self.client.storage.from_(self.bucket).download(path=key)
        except Exception as exc:
            raise RuntimeError(f"Failed to download '{key}' from bucket '{self.bucket}'.") from exc
        if hasattr(response, "content"):
            return response.content
        return response

    def delete(self, relative_path):
        key = self._path_to_key(relative_path)
        try:
            self.client.storage.from_(self.bucket).remove([key])
            return True
        except Exception:
            return False

    def initialize_bucket(self):
        """Create the configured bucket if it does not already exist."""
        try:
            buckets = self.client.storage.list_buckets()
            existing = [bucket.get("name") for bucket in buckets.get("data", []) if bucket.get("name")]
            if self.bucket not in existing:
                self.client.storage.create_bucket(self.bucket)
            return True
        except Exception:
            return False

    def exists(self, relative_path):
        try:
            self.client.storage.from_(self.bucket).list(path=self._path_to_key(Path(relative_path).parent))
            return any(Path(item.get("name", "")) == Path(relative_path).name for item in self.list_files(Path(relative_path).parent.as_posix()))
        except Exception:
            return False

    def save_dataframe(self, dataframe: pd.DataFrame, relative_path):
        with tempfile.NamedTemporaryFile(
            suffix=".xlsx",
            delete=False
        ) as tmp:
            temp_path = Path(tmp.name)
        try:
            dataframe.to_excel(temp_path, index=False)

            with open(temp_path,"rb") as handle:
                self.write_bytes(relative_path, handle.read())
        finally:
            if temp_path.exists():
                temp_path.unlink()
        
        return self.resolve(relative_path)

    def load_dataframe(self, relative_path):
        data = self.read_bytes(relative_path)
        if isinstance(data, bytes):
            path = self.resolve(relative_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            return pd.read_excel(path)
        return pd.read_excel(data)


def create_storage(backend=None,root=None,url=None,key=None,bucket=None,):
    """Instantiate a storage backend."""

    backend_name = (backend or os.getenv("ATTENDANCE_STORAGE_BACKEND") or "local").lower()
    storage_root = root or os.getenv("ATTENDANCE_STORAGE_ROOT")

    if backend_name in {"cloud", "supabase"}:
        return SupabaseStorage(root=storage_root,url=url,key=key,bucket=bucket,)

    if backend_name in {"local", "filesystem", "file"}:
        return LocalStorage(storage_root or Path.cwd())

    raise ValueError(f"Unsupported storage backend: {backend_name}")

def initialize_storage_backend(backend=None, root=None, url=None, key=None, bucket=None):
    """Create and initialize the configured storage backend."""
    storage = create_storage(backend=backend, root=root, url=url, key=key,bucket=bucket)
    if isinstance(storage, SupabaseStorage):
        storage.initialize_bucket()
    return storage


def migrate_local_files_to_storage(storage, source_root=None):
    """Upload existing local repository files into the configured storage backend."""
    if source_root is None:
        source_root = Path("data")

    source_root = Path(source_root)
    if not source_root.exists():
        return []

    migrated = []

    for path in source_root.rglob("*"):
        if not path.is_file():
            continue

        relative_path = path.relative_to(source_root)
        with path.open("rb") as handle:
            storage.write_bytes(str(relative_path).replace("\\", "/"), handle.read())
        migrated.append(str(relative_path))

    return migrated
