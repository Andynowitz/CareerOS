from __future__ import annotations

from uuid import UUID

from app.ai.analyzers.job_analyzer import JobAnalyzer
from app.ai.client import AIClient
from app.models.job_analysis import JobAnalysis
from app.repositories.job_analysis import JobAnalysisRepository


class JobAnalysisService:
    def __init__(
        self,
        analyzer: JobAnalyzer,
        repository: JobAnalysisRepository,
    ) -> None:
        self.analyzer = analyzer
        self.repository = repository

    async def analyze_job(
        self,
        job_id: UUID,
        job_description: str,
    ) -> JobAnalysis:
        result = await self.analyzer.analyze(job_description)

        analysis = JobAnalysis(
            job_id=job_id,
            required_skills=result.required_skills,
            preferred_skills=result.preferred_skills,
            responsibilities=result.responsibilities,
            experience_requirements=result.experience_requirements,
            education_requirements=result.education_requirements,
            keywords=result.keywords,
            salary_information=result.salary_information,
            raw_analysis=result.model_dump(),
        )

        return await self.repository.create(analysis)