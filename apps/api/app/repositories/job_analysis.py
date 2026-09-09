from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_analysis import JobAnalysis


class JobAnalysisRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        analysis: JobAnalysis,
    ) -> JobAnalysis:
        self.session.add(analysis)
        await self.session.commit()
        await self.session.refresh(analysis)

        return analysis

    async def get_latest_for_job(
        self,
        job_id: UUID,
    ) -> JobAnalysis | None:
        result = await self.session.execute(
            select(JobAnalysis)
            .where(JobAnalysis.job_id == job_id)
            .order_by(JobAnalysis.created_at.desc())
            .limit(1)
        )

        return result.scalar_one_or_none()