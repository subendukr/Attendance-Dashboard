import logging
import os
import tempfile
from datetime import datetime
from io import BytesIO
import json

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

import pandas as pd

DEFAULT_STORAGE_ROOT = "data"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STORAGE_ROOT = PROJECT_ROOT / "data"

try:
    from supabase import create_client
except ImportError:
    create_client = None

logger = logging.getLogger(__name__)

if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

class StorageError(Exception):
    """Base class for storage-related errors."""


class StorageConfigurationError(StorageError):
    """Raised when storage is incorrectly configured."""


class StorageUploadError(StorageError):
    """Raised when upload fails."""


class StorageDownloadError(StorageError):
    """Raised when download fails."""


class StorageAdapter(ABC):
    """
    Abstract storage interface.

    Every storage backend (Local, Supabase, S3, Azure...)
    must implement these methods.
    """

    @abstractmethod
    def ensure_directory(self, *parts):
        pass

    @abstractmethod
    def resolve(self, *parts):
        pass

    @abstractmethod
    def list_files(self, relative_dir=".", pattern="*"):
        pass

    @abstractmethod
    def write_bytes(self, relative_path, content):
        pass

    @abstractmethod
    def read_bytes(self, relative_path):
        pass

    @abstractmethod
    def delete(self, relative_path):
        pass

    @abstractmethod
    def exists(self, relative_path):
        pass

    @abstractmethod
    def last_modified(self, relative_path):
        pass

    @abstractmethod
    def save_dataframe(
        self,
        dataframe: pd.DataFrame,
        relative_path: str,
    ):
        pass

    @abstractmethod
    def load_dataframe(
        self,
        relative_path: str,
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def load_csv(
        self,
        relative_path: str,
    ) -> pd.DataFrame:
        """
        Load a CSV into a DataFrame.
        """
        raise NotImplementedError
    
    @abstractmethod
    def save_csv(
        self,
        dataframe: pd.DataFrame,
        relative_path: str,
    ):
        """
        Save a DataFrame as CSV.
        """
        raise NotImplementedError
    
    def open_excel(self, relative_path: str):
        """
        Return a pandas.ExcelFile object.
        """
        raise NotImplementedError
    
    def read_excel(
        self,
        relative_path: str,
        **kwargs,
    ):
        """
        Read an Excel sheet into a DataFrame.
        """
        raise NotImplementedError
    
    @abstractmethod
    def load_json(self, relative_path: str):
        """
        Load a JSON object from storage.

        Parameters
        ----------
        relative_path
            Repository-relative JSON path.

        Returns
        -------
        dict | list
            Parsed JSON object.
        """
        raise NotImplementedError

    @abstractmethod
    def save_json(
        self,
        data,
        relative_path: str,
    ):
        """
        Persist a JSON object.

        Parameters
        ----------
        data
            Dictionary or list to serialize.

        relative_path
            Repository-relative path.

        Returns
        -------
        Storage-specific saved location.
        """
        raise NotImplementedError


class LocalStorage(StorageAdapter):
    """
    Local filesystem implementation.

    This implementation mirrors the behaviour expected by the
    repository while keeping all filesystem logic isolated.
    """

    def __init__(self, root: Union[str, Path]):
        self.root = Path(root).resolve()

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

        return sorted(
            p
            for p in directory.glob(pattern)
            if p.is_file()
        )

    def write_bytes(self, relative_path, content, overwrite=True):
        path = self.resolve(relative_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(content)

        return path

    def read_bytes(
        self,
        relative_path,
    ):
        path = self.resolve(relative_path)

        if not path.exists():
            raise StorageDownloadError(
                f"{path} does not exist."
            )

        return path.read_bytes()

    def delete(
        self,
        relative_path,
    ):
        path = self.resolve(relative_path)

        if not path.exists():
            return False

        path.unlink()

        return True

    def exists(self, relative_path):
        return self.resolve(relative_path).exists()
    
    def last_modified(self, relative_path):
        path = self.resolve(relative_path)

        if not path.exists():
            return None

        return datetime.fromtimestamp(
            path.stat().st_mtime
        )

    def save_dataframe(
        self,
        dataframe,
        relative_path,
    ):
        path = self.resolve(relative_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        dataframe.to_excel(
            path,
            index=False,
        )

        return path

    def load_dataframe(
        self,
        relative_path,
    ):
        path = self.resolve(relative_path)

        if not path.exists():
            raise StorageDownloadError(
                f"{path} does not exist."
            )

        return pd.read_excel(path)
    
    def save_csv(
        self,
        dataframe: pd.DataFrame,
        relative_path: str,
    ):
        path = self.resolve(relative_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        dataframe.to_csv(
            path,
            index=False,
        )

        return path
    
    # ==========================================
    # CSV
    # ==========================================

    def load_csv(self, relative_path: str):
        path = self.resolve(relative_path)

        if not path.exists():
            raise FileNotFoundError(path)

        return pd.read_csv(path)

    # ==========================================
    # Excel
    # ==========================================

    def open_excel(self, relative_path):
        path = self.resolve(relative_path)
        return pd.ExcelFile(path)


    def read_excel(self, relative_path, **kwargs):
        path = self.resolve(relative_path)
        return pd.read_excel(path, **kwargs)
        
    # ==========================================
    # JSON
    # ==========================================
    
    def load_json(self, relative_path: str):
        """
        Load a JSON object from local storage.
        """

        path = self.resolve(relative_path)

        if not path.exists():
            raise StorageDownloadError(
                f"{path} does not exist."
            )

        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
   
    def save_json(
        self,
        data,
        relative_path: str,
    ):
        """
        Save a JSON object to local storage.
        """

        path = self.resolve(relative_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return path


class SupabaseStorage(StorageAdapter):
    """
    Supabase implementation of the StorageAdapter.

    All direct communication with Supabase Storage is isolated
    inside this class.
    """

    def __init__(self,root=None,url=None,key=None,bucket=None):
        self.root = Path(root) if root else Path.cwd()
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        self.bucket = bucket or os.getenv("SUPABASE_BUCKET", "attendance")
        if not self.url:
            raise StorageConfigurationError("SUPABASE_URL is missing.")
        if not self.key:
            raise StorageConfigurationError("SUPABASE_KEY is missing.")
        if create_client is None:
            raise StorageConfigurationError("supabase package is not installed.")

        self._client = create_client(self.url,self.key)
        logger.info("Initialized SupabaseStorage (%s)",self.bucket )

    @property
    def client(self):
        """Return the initialized Supabase client."""
        return self._client
    
    def _storage(self):
        """
        Return the configured Supabase bucket.
        """
        return self.client.storage.from_(self.bucket)

    def ensure_directory(self, *parts):
        return self.resolve(*parts)

    def resolve(self, *parts):
        return Path(*parts)

    def _path_to_key(self, relative_path):
        """
        Convert a filesystem path into a
        Supabase Storage object key.
        """
        return str(Path(relative_path).as_posix())
    
    def _upload(
        self,
        key,
        content,
        overwrite=True,
    ):
        if isinstance(content, memoryview):
            content = content.tobytes()

        try:
            options = None

            if overwrite:
                options = {
                    "upsert": "true"
                }

            self._storage().upload(
                path=key,
                file=content,
                file_options=options,
            )

        except Exception as exc:
            logger.exception("Upload failed: %s", key)

            raise StorageUploadError(
                f"Unable to upload '{key}'."
            ) from exc
        
    def _download(self, key):
        try:
            response = self._storage().download(
            path=key,
            )

            if hasattr(response, "content"):
                return response.content

            return response

        except Exception as exc:
            logger.exception("Download failed: %s", key)

            raise StorageDownloadError(
                f"Unable to download '{key}'."
            ) from exc
        
    def _remove(self, key):
        try:
            self._storage().remove([key])

        except Exception as exc:
            logger.exception("Delete failed: %s", key)

            raise StorageError(
                f"Unable to delete '{key}'."
            ) from exc

    def _list(self, path=""):
        try:
            return self._storage().list(path=path)
        
        except Exception:
            logger.exception("List failed: %s", path) 
            return []

    def list_files(self,relative_dir=".",pattern="*"):
        # "." means bucket root in the repository.
        if str(relative_dir) in (".", ""):
            path = ""
        else:
            path = self._path_to_key(relative_dir)

        items = self._list(path)

        return [
            Path(item["name"])
            for item in items
            if item.get("name")
        ]

    def write_bytes(
        self,
        relative_path,
        content,
        overwrite=True,
    ):
        key = self._path_to_key(relative_path)

        self._upload(
            key=key,
            content=content,
            overwrite=overwrite,
        )

        return self.resolve(relative_path)

    def read_bytes(self, relative_path):
        key = self._path_to_key(relative_path)
        return self._download(key)

    def delete(self, relative_path):
        key = self._path_to_key(relative_path)
        self._remove(key)
        return True

    def initialize_bucket(self):
        """
        Create the bucket if it
        does not already exist.
        """

        try:

            buckets = self.client.storage.list_buckets()

            existing = {
                bucket.name
                if hasattr(bucket, "name")
                else bucket.get("name")
                for bucket in buckets
            }

            if self.bucket not in existing:
                logger.info("Creating bucket %s",self.bucket)
                self.client.storage.create_bucket(self.bucket)
            return True

        except Exception:
            logger.exception("Unable to initialize bucket.")
            return False

    def exists(
        self,
        relative_path,
    ):
        parent = Path(relative_path).parent
        filename = Path(relative_path).name

        if str(parent) == ".":
            parent = ""

        files = self.list_files(parent)

        # ---------- TEMPORARY DEBUG ----------
        logger.info(
            "Checking %s in '%s' -> %s",
            filename,
            parent,
            [f.name for f in files],
        )
    # -------------------------------------

        return any(
            f.name == filename
            for f in files
        )
    
    def last_modified(self, relative_path):
        """
        Return the last modified timestamp of a Supabase object.

        Currently not implemented.
        """

        return None

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
        return pd.read_excel(BytesIO(data))
    
    # ==========================================
    # CSV
    # ==========================================
    
    def save_csv(
        self,
        dataframe: pd.DataFrame,
        relative_path: str,
    ):
        csv_bytes = dataframe.to_csv(
            index=False,
        ).encode("utf-8")

        self.write_bytes(
            relative_path,
            csv_bytes,
        )

        return self.resolve(relative_path)

    def load_csv(
        self,
        relative_path: str,
    ):
        data = self.read_bytes(
            relative_path,
        )

        dataframe = pd.read_csv(
            BytesIO(data),
        )

        return dataframe
    

    # ==========================================
    # EXCEL
    # ==========================================

    def open_excel(self, relative_path):
        data = self.read_bytes(relative_path)
        return pd.ExcelFile(BytesIO(data))


    def read_excel(self,relative_path,**kwargs):
        data = self.read_bytes(relative_path)
        return pd.read_excel(BytesIO(data), **kwargs)

    # ==========================================
    # JSON
    # ==========================================
    
    def load_json(self, relative_path: str):
        """
        Load a JSON object from Supabase storage.
        """

        content = self.read_bytes(relative_path)

        return json.loads(
            content.decode("utf-8")
        )
    
    def save_json(
        self,
        data,
        relative_path: str,
    ):
        """
        Save a JSON object to Supabase storage.
        """

        content = json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ).encode("utf-8")

        self.write_bytes(
            relative_path,
            content,
        )

        return self.resolve(relative_path)

def create_storage(backend=None,root=None,url=None,key=None,bucket=None):
    """
    Factory function that creates the configured storage backend.
    """

    backend_name = (
        backend 
        or os.getenv("ATTENDANCE_STORAGE_BACKEND")
        or "local"
    ).lower()

    storage_root = (Path(root) if root else Path(os.getenv("ATTENDANCE_STORAGE_ROOT", DEFAULT_STORAGE_ROOT)))

    if backend_name in {"local", "filesystem", "file"}:
        return LocalStorage(storage_root)
    if backend_name in {"cloud", "supabase"}:
        return SupabaseStorage(root=storage_root,url=url,key=key,bucket=bucket)

    raise StorageConfigurationError(f"Unsupported storage backend '{backend_name}'.")

def initialize_storage_backend(
    backend=None,
    root=None,
    url=None,
    key=None,
    bucket=None,
):
    """
    Create and initialize the configured storage backend.
    """

    storage = create_storage(
        backend=backend,
        root=root,
        url=url,
        key=key,
        bucket=bucket,
    )

    if isinstance(storage, SupabaseStorage):

        logger.info(
            "Initializing bucket '%s'",
            storage.bucket,
        )

        storage.initialize_bucket()

    return storage


def migrate_local_files_to_storage(
    storage,
    source_root=None,
):
    """
    Upload every file from a local repository into
    the configured storage backend.
    """

    source_root = Path(source_root or "data")

    if not source_root.exists():

        logger.warning(
            "Migration source '%s' does not exist.",
            source_root,
        )

        return []

    migrated = []

    files = sorted(
        path
        for path in source_root.rglob("*")
        if path.is_file()
    )

    logger.info(
        "Migrating %d files...",
        len(files),
    )

    for file_path in files:

        relative = file_path.relative_to(source_root)

        relative_key = str(relative).replace("\\", "/")

        if storage.exists(relative_key):
            logger.info(
                "Skipping existing file: %s",
                relative_key,
            )
            continue

        with file_path.open("rb") as handle:
            storage.write_bytes(
                relative_key,
                handle.read(),
            )

        migrated.append(relative_key)


    logger.info(
        "Migration complete (%d files).",
        len(migrated),
    )

    return migrated
