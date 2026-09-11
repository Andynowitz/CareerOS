from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_insight import JobInsight


class JobInsightRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, insight: JobInsight) -> JobInsight:
        self.session.add(insight)
        await self.session.commit()
        await self.session.refresh(insight)
        return insight

    async def get_latest_for_job_and_resume(
        self,
        job_id: UUID,
        resume_id: UUID,
    ) -> JobInsight | None:
        result = await self.session.execute(
            select(JobInsight)
            .where(
                JobInsight.job_id == job_id,
                JobInsight.resume_id == resume_id,
            )
            .order_by(JobInsight.created_at.desc())
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def get_history_for_job_and_resume(
        self,
        job_id: UUID,
        resume_id: UUID,
    ) -> list[JobInsight]:
        result = await self.session.execute(
            select(JobInsight)
            .where(
                JobInsight.job_id == job_id,
                JobInsight.resume_id == resume_id,
            )
            .order_by(JobInsight.created_at.desc())
        )

        return list(result.scalars().all())