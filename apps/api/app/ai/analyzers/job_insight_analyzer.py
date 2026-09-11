from __future__ import annotations

from pydantic import BaseModel, Field

from app.ai.client import AIClient

from typing import Any

class JobInsightResult(BaseModel):
    match_score: int = Field(ge=0, le=100)

    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)

    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)

    recommendations: list[str] = Field(default_factory=list)

    overall_assessment: str | None = None


class JobInsightAnalyzer:
    def __init__(self, client: AIClient) -> None:
        self.client = client

    async def analyze(
        self,
        job_analysis: dict[str, Any],
        resume_analysis: dict[str, Any],
    ) -> JobInsightResult:
        prompt = f"""
Analyze how well the resume matches the job.

Compare the job requirements with the candidate's resume.

Evaluate:

1. Overall match score from 0 to 100
2. Skills that match the job requirements
3. Skills required by the job that are missing from the resume
4. Candidate strengths relevant to this job
5. Candidate weaknesses or gaps relevant to this job
6. Concrete recommendations for improving the application
7. A concise overall assessment

Important rules:

- Base the analysis only on the information provided.
- Do not invent skills, experience, education, or projects.
- Missing information should not be treated as confirmed experience.
- The match score must be between 0 and 100.
- Focus on relevance to this specific job.

Job analysis:
{job_analysis}

Resume analysis:
{resume_analysis}
"""

        return await self.client.analyze(
            prompt,
            JobInsightResult,
        )