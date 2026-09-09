from __future__ import annotations

from pydantic import BaseModel, Field

from app.ai.client import AIClient
from app.ai.prompts import RESUME_ANALYSIS_PROMPT


class ResumeAnalysisResult(BaseModel):
    skills: list[str] = Field(default_factory=list)

    experience_summary: str | None = None
    education_summary: str | None = None
    projects_summary: str | None = None


class ResumeAnalyzer:
    def __init__(self, client: AIClient) -> None:
        self.client = client

    async def analyze(
        self,
        resume_text: str,
    ) -> ResumeAnalysisResult:
        prompt = RESUME_ANALYSIS_PROMPT.format(
            resume_text=resume_text,
        )

        return await self.client.analyze(
            prompt,
            ResumeAnalysisResult,
        )