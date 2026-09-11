from __future__ import annotations

import asyncio
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.ai.analyzers.job_insight_analyzer import JobInsightAnalyzer
from app.ai.client import AIClient
from app.core.config import get_settings
from app.models.job import Job
from app.models.resume import Resume
from app.repositories.job_analysis import JobAnalysisRepository
from app.repositories.job_insight import JobInsightRepository
from app.repositories.resume_analysis import ResumeAnalysisRepository
from app.services.job_insight import JobInsightService
from app.tasks.celery_app import celery_app

from typing import Any

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)  # type: ignore[misc]
def analyze_job_insight_task(
    self: Any,
    job_id: str,
    resume_id: str,
) -> str:
    try:
        return asyncio.run(
            _run_analysis(
                job_id=job_id,
                resume_id=resume_id,
            )
        )
    except ValueError:
        # Permanent errors should not be retried.
        raise
    except Exception as exc:
        # Retry potentially temporary infrastructure/AI failures.
        raise self.retry(
            exc=exc,
            countdown=5 * (2 ** self.request.retries),
        )


async def _run_analysis(
    job_id: str,
    resume_id: str,
) -> str:
    settings = get_settings()

    engine = create_async_engine(
        settings.database_url,
        poolclass=NullPool,
    )

    SessionLocal = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    try:
        async with SessionLocal() as session:
            job_result = await session.execute(
                select(Job).where(Job.id == UUID(job_id))
            )
            job = job_result.scalar_one_or_none()

            if job is None:
                raise ValueError(f"Job {job_id} not found")

            resume_result = await session.execute(
                select(Resume).where(Resume.id == UUID(resume_id))
            )
            resume = resume_result.scalar_one_or_none()

            if resume is None:
                raise ValueError(f"Resume {resume_id} not found")

            job_analysis_repository = JobAnalysisRepository(session)
            resume_analysis_repository = ResumeAnalysisRepository(session)

            job_analysis = await job_analysis_repository.get_latest_for_job(
                job.id
            )

            if job_analysis is None:
                raise ValueError(
                    f"No job analysis found for job {job_id}"
                )

            resume_analysis = (
                await resume_analysis_repository.get_latest_for_resume(
                    resume.id
                )
            )

            if resume_analysis is None:
                raise ValueError(
                    f"No resume analysis found for resume {resume_id}"
                )

            client = AIClient()
            analyzer = JobInsightAnalyzer(client)
            repository = JobInsightRepository(session)

            service = JobInsightService(
                analyzer=analyzer,
                repository=repository,
            )

            await service.analyze_job(
                job_id=job.id,
                resume_id=resume.id,
                job_analysis=job_analysis.raw_analysis or {},
                resume_analysis=resume_analysis.raw_analysis or {},
            )

            return f"{job_id}:{resume_id}"

    finally:
        await engine.dispose()