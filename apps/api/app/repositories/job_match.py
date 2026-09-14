from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_match import JobMatch


class JobMatchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        job_id: uuid.UUID,
        resume_id: uuid.UUID,
        score: int,
        required_skills_score: float,
        preferred_skills_score: float,
        experience_score: float,
        education_score: float,
        keywords_score: float,
        matched_required_skills: list[str],
        missing_required_skills: list[str],
        matched_preferred_skills: list[str],
        missing_preferred_skills: list[str],
        explanations: list[str],
    ) -> JobMatch:
        match = JobMatch(
            job_id=job_id,
            resume_id=resume_id,
            score=score,
            required_skills_score=required_skills_score,
            preferred_skills_score=preferred_skills_score,
            experience_score=experience_score,
            education_score=education_score,
            keywords_score=keywords_score,
            matched_required_skills=matched_required_skills,
            missing_required_skills=missing_required_skills,
            matched_preferred_skills=matched_preferred_skills,
            missing_preferred_skills=missing_preferred_skills,
            explanations=explanations,
        )

        self.session.add(match)
        await self.session.flush()

        return match

    async def get_by_id(
        self,
        match_id: uuid.UUID,
    ) -> JobMatch | None:
        result = await self.session.execute(
            select(JobMatch).where(JobMatch.id == match_id)
        )

        return result.scalar_one_or_none()

    async def get_latest(
        self,
        *,
        job_id: uuid.UUID,
        resume_id: uuid.UUID,
    ) -> JobMatch | None:
        result = await self.session.execute(
            select(JobMatch)
            .where(
                JobMatch.job_id == job_id,
                JobMatch.resume_id == resume_id,
            )
            .order_by(JobMatch.created_at.desc())
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def list_history(
        self,
        *,
        job_id: uuid.UUID,
        resume_id: uuid.UUID,
    ) -> list[JobMatch]:
        result = await self.session.execute(
            select(JobMatch)
            .where(
                JobMatch.job_id == job_id,
                JobMatch.resume_id == resume_id,
            )
            .order_by(JobMatch.created_at.desc())
        )

        return list(result.scalars().all())