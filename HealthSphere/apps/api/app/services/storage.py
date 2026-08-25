"""File storage abstraction: local filesystem (default) or S3-compatible."""
import hashlib
import os
import uuid
from pathlib import Path

from app.core.config import settings


class StorageService:
    provider: str = "local"

    def save(self, content: bytes, user_id: int, original_name: str) -> str:
        raise NotImplementedError

    def read(self, storage_key: str) -> bytes:
        raise NotImplementedError

    def delete(self, storage_key: str) -> None:
        raise NotImplementedError


def _safe_ext(original_name: str) -> str:
    ext = Path(original_name).suffix.lower()
    return ext if ext in {".pdf", ".jpg", ".jpeg", ".png"} else ""


class LocalStorageService(StorageService):
    provider = "local"

    def __init__(self) -> None:
        self.root = Path(settings.local_storage_path).resolve()

    def _path_for(self, storage_key: str) -> Path:
        # storage_key format: "user-<id>/<uuid>.<ext>" — prevent traversal
        if ".." in storage_key or storage_key.startswith("/"):
            raise ValueError("Invalid storage key")
        return self.root / storage_key

    def save(self, content: bytes, user_id: int, original_name: str) -> str:
        ext = _safe_ext(original_name)
        key = f"user-{user_id}/{uuid.uuid4().hex}{ext}"
        path = self._path_for(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return key

    def read(self, storage_key: str) -> bytes:
        return self._path_for(storage_key).read_bytes()

    def delete(self, storage_key: str) -> None:
        path = self._path_for(storage_key)
        if path.exists():
            os.remove(path)


class S3StorageService(StorageService):
    """S3-compatible storage (AWS S3 / MinIO). Requires boto3 at runtime."""

    provider = "s3"

    def __init__(self) -> None:
        import boto3  # lazy import; optional dependency

        self.bucket = settings.storage_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.storage_endpoint or None,
            aws_access_key_id=settings.storage_access_key,
            aws_secret_access_key=settings.storage_secret_key,
        )

    @staticmethod
    def _key(user_id: int, original_name: str) -> str:
        ext = _safe_ext(original_name)
        digest = hashlib.sha256(os.urandom(32)).hexdigest()[:24]
        return f"user-{user_id}/{digest}{ext}"

    def save(self, content: bytes, user_id: int, original_name: str) -> str:
        key = self._key(user_id, original_name)
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content)
        return key

    def read(self, storage_key: str) -> bytes:
        resp = self.client.get_object(Bucket=self.bucket, Key=storage_key)
        return resp["Body"].read()

    def delete(self, storage_key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=storage_key)


def get_storage() -> StorageService:
    if settings.storage_provider == "s3":
        return S3StorageService()
    return LocalStorageService()
