from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ResumeAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resume_id: UUID
    skills: list[str]
    experience_summary: str | None
    education_summary: str | None
    projects_summary: str | None
    raw_analysis: dict[str, Any] | None
    created_at: datetime