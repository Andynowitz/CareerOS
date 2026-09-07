from __future__ import annotations

import io
from uuid import UUID

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings


class ResumeStorageError(Exception):
    """Raised when resume storage operations fail."""


class ResumeStorage:
    def __init__(self) -> None:
        settings = get_settings()

        self.bucket = settings.minio_bucket
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=settings.minio_secure,
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as exc:
            raise ResumeStorageError(
                "Could not initialize MinIO bucket"
            ) from exc

    def put(
        self,
        data: io.BytesIO,
        size: int,
        content_type: str,
        user_id: str,
        resume_id: UUID,
        version: int,
    ) -> str:
        object_key = f"{user_id}/{resume_id}/v{version}"

        try:
            self.client.put_object(
                self.bucket,
                object_key,
                data,
                length=size,
                content_type=content_type,
            )
        except S3Error as exc:
            raise ResumeStorageError(
                "Could not store resume"
            ) from exc

        return object_key

    def get(self, object_key: str):
        try:
            return self.client.get_object(
                self.bucket,
                object_key,
            )
        except S3Error as exc:
            raise ResumeStorageError(
                "Could not retrieve resume"
            ) from exc

    def delete(self, object_key: str) -> None:
        try:
            self.client.remove_object(
                self.bucket,
                object_key,
            )
        except S3Error as exc:
            raise ResumeStorageError(
                "Could not delete resume"
            ) from exc