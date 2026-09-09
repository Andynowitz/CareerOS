from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume_analysis import ResumeAnalysis


class ResumeAnalysisRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        analysis: ResumeAnalysis,
    ) -> ResumeAnalysis:
        self.session.add(analysis)
        await self.session.commit()
        await self.session.refresh(analysis)

        return analysis

    async def get_latest_for_resume(
        self,
        resume_id: UUID,
    ) -> ResumeAnalysis | None:
        result = await self.session.execute(
            select(ResumeAnalysis)
            .where(ResumeAnalysis.resume_id == resume_id)
            .order_by(ResumeAnalysis.created_at.desc())
            .limit(1)
        )

        return result.scalar_one_or_none()