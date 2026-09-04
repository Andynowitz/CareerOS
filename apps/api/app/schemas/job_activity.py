from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.job_activity import JobActivityType


class JobActivityCreate(BaseModel):
    type: JobActivityType
    description: str | None = Field(default=None, max_length=5000)


class JobActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    user_id: str
    type: JobActivityType
    description: str | None
    old_status: str | None
    new_status: str | None
    created_at: datetime