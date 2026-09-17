from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_activity import JobActivity


class JobActivityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, activity: JobActivity) -> JobActivity:
        self.session.add(activity)
        await self.session.commit()
        await self.session.refresh(activity)
        return activity

    async def get_all(
        self,
        job_id: UUID,
        user_id: str,
    ) -> list[JobActivity]:
        result = await self.session.execute(
            select(JobActivity)
            .where(
                JobActivity.job_id == job_id,
                JobActivity.user_id == user_id,
            )
            .order_by(JobActivity.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        activity_id: UUID,
        user_id: str,
    ) -> JobActivity | None:
        result = await self.session.execute(
            select(JobActivity).where(
                JobActivity.id == activity_id,
                JobActivity.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_all_for_user(
        self,
        user_id: str,
    ) -> list[JobActivity]:
        result = await self.session.execute(
            select(JobActivity)
            .where(
                JobActivity.user_id == user_id,
            )
            .order_by(JobActivity.created_at.desc())
        )

        return list(result.scalars().all())
    