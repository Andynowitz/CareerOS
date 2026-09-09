from __future__ import annotations

from uuid import UUID

from app.ai.analyzers.resume_analyzer import ResumeAnalyzer
from app.models.resume_analysis import ResumeAnalysis
from app.repositories.resume_analysis import ResumeAnalysisRepository


class ResumeAnalysisService:
    def __init__(
        self,
        analyzer: ResumeAnalyzer,
        repository: ResumeAnalysisRepository,
    ) -> None:
        self.analyzer = analyzer
        self.repository = repository

    async def analyze_resume(
        self,
        resume_id: UUID,
        resume_text: str,
    ) -> ResumeAnalysis:
        result = await self.analyzer.analyze(resume_text)

        analysis = ResumeAnalysis(
            resume_id=resume_id,
            skills=result.skills,
            experience_summary=result.experience_summary,
            education_summary=result.education_summary,
            projects_summary=result.projects_summary,
            raw_analysis=result.model_dump(),
        )

        return await self.repository.create(analysis)