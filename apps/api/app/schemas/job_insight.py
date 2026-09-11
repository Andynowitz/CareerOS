from __future__ import annotations

from datetime import datetime
from uuid import UUID

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobInsightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    resume_id: UUID

    match_score: int = Field(ge=0, le=100)

    matching_skills: list[str]
    missing_skills: list[str]

    strengths: list[str]
    weaknesses: list[str]

    recommendations: list[str]

    overall_assessment: str | None

    raw_insight: dict[str, Any] | None
    
    created_at: datetime