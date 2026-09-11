from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    required_skills: list[str]
    preferred_skills: list[str]
    responsibilities: list[str]
    experience_requirements: str | None
    education_requirements: str | None
    keywords: list[str]
    salary_information: dict[str, Any] | None
    raw_analysis: dict[str, Any] | None
    created_at: datetime