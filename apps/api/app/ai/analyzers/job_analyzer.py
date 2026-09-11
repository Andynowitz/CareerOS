from __future__ import annotations

from pydantic import BaseModel, Field

from app.ai.client import AIClient
from app.ai.prompts import JOB_ANALYSIS_PROMPT


class JobAnalysisResult(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)

    experience_requirements: str | None = None
    education_requirements: str | None = None

    keywords: list[str] = Field(default_factory=list)

    salary_information: dict[str, str | int | float | None] | None = None


class JobAnalyzer:
    def __init__(self, client: AIClient) -> None:
        self.client = client

    async def analyze(
        self,
        job_description: str,
    ) -> JobAnalysisResult:
        prompt = JOB_ANALYSIS_PROMPT.format(
            job_description=job_description,
        )

        return await self.client.analyze(
            prompt,
            JobAnalysisResult,
        )