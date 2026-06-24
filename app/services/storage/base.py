"""Object storage abstractions."""

from abc import ABC, abstractmethod
from pathlib import Path


class StorageBackend(ABC):
    """Abstract file storage interface (local disk or S3-compatible)."""

    @abstractmethod
    async def save(self, *, relative_path: str, content: bytes) -> str:
        """Persist bytes and return the storage path."""

    @abstractmethod
    async def read(self, storage_path: str) -> bytes:
        """Read file contents from storage."""

    @abstractmethod
    async def delete(self, storage_path: str) -> None:
        """Remove a stored file."""

    @abstractmethod
    async def exists(self, storage_path: str) -> bool:
        """Return True if the file exists in storage."""


class LocalStorageBackend(StorageBackend):
    """Store files on the local filesystem."""

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve(self, storage_path: str) -> Path:
        """Resolve and validate path stays within base directory."""
        full_path = (self._base_dir / storage_path).resolve()
        if not str(full_path).startswith(str(self._base_dir.resolve())):
            from app.exceptions import ValidationError

            raise ValidationError("Invalid storage path")
        return full_path

    async def save(self, *, relative_path: str, content: bytes) -> str:
        """Write content to disk under the configured base directory."""
        target = self._resolve(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return relative_path

    async def read(self, storage_path: str) -> bytes:
        """Read bytes from disk."""
        return self._resolve(storage_path).read_bytes()

    async def delete(self, storage_path: str) -> None:
        """Delete a file from disk if it exists."""
        path = self._resolve(storage_path)
        if path.exists():
            path.unlink()

    async def exists(self, storage_path: str) -> bool:
        """Check whether the file exists on disk."""
        return self._resolve(storage_path).exists()
