from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, job: Job) -> Job:
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_by_id(self, job_id: UUID, user_id: str) -> Job | None:
        result = await self.session.execute(
            select(Job).where(
                Job.id == job_id,
                Job.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, user_id: str) -> list[Job]:
        result = await self.session.execute(
            select(Job)
            .where(Job.user_id == user_id)
            .order_by(Job.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, job: Job) -> Job:
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def delete(self, job: Job) -> None:
        await self.session.delete(job)
        await self.session.commit()