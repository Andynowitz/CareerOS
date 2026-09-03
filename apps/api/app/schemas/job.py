from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.job import JobStatus


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company: str = Field(min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    url: HttpUrl | None = None
    description: str | None = None
    status: JobStatus = JobStatus.SAVED


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    company: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    url: HttpUrl | None = None
    description: str | None = None
    status: JobStatus | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    title: str
    company: str
    location: str | None
    url: str | None
    description: str | None
    status: JobStatus
    created_at: datetime
    updated_at: datetime