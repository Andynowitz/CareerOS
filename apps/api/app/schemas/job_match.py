from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class JobMatchCreateRequest(BaseModel):
    resume_id: UUID = Field(
        description="ID of the resume to match against the job.",
    )

class JobMatchResponse(BaseModel):
    id: UUID
    job_id: UUID
    resume_id: UUID

    score: int = Field(ge=0, le=100)

    required_skills_score: float = Field(ge=0.0, le=1.0)
    preferred_skills_score: float = Field(ge=0.0, le=1.0)
    experience_score: float = Field(ge=0.0, le=1.0)
    education_score: float = Field(ge=0.0, le=1.0)
    keywords_score: float = Field(ge=0.0, le=1.0)

    matched_required_skills: list[str]
    missing_required_skills: list[str]

    matched_preferred_skills: list[str]
    missing_preferred_skills: list[str]

    explanations: list[str]

    created_at: datetime


class JobMatchHistoryResponse(BaseModel):
    matches: list[JobMatchResponse]