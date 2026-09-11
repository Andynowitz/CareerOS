from __future__ import annotations

from uuid import UUID

from app.ai.analyzers.job_insight_analyzer import JobInsightAnalyzer
from app.models.job_insight import JobInsight
from app.repositories.job_insight import JobInsightRepository


class JobInsightService:
    def __init__(
        self,
        analyzer: JobInsightAnalyzer,
        repository: JobInsightRepository,
    ) -> None:
        self.analyzer = analyzer
        self.repository = repository

    async def analyze_job(
        self,
        job_id: UUID,
        resume_id: UUID,
        job_analysis: dict,
        resume_analysis: dict,
    ) -> JobInsight:
        result = await self.analyzer.analyze(
            job_analysis=job_analysis,
            resume_analysis=resume_analysis,
        )

        insight = JobInsight(
            job_id=job_id,
            resume_id=resume_id,
            match_score=result.match_score,
            matching_skills=result.matching_skills,
            missing_skills=result.missing_skills,
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            recommendations=result.recommendations,
            overall_assessment=result.overall_assessment,
            raw_insight=result.model_dump(),
        )

        return await self.repository.create(insight)