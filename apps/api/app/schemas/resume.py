from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ResumeVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resume_id: UUID
    version: int
    filename: str
    content_type: str
    size_bytes: int
    extracted_text: str | None
    created_at: datetime


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    name: str
    current_version: int
    created_at: datetime
    updated_at: datetime


class ResumeDetailResponse(ResumeResponse):
    versions: list[ResumeVersionResponse]