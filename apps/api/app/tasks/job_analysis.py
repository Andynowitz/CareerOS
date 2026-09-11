import asyncio
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.ai.analyzers.job_analyzer import JobAnalyzer
from app.ai.client import AIClient
from app.core.config import get_settings
from app.models.job import Job
from app.repositories.job_analysis import JobAnalysisRepository
from app.services.job_analysis import JobAnalysisService
from app.tasks.celery_app import celery_app

from typing import Any

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)  # type: ignore[misc]
def analyze_job_task(self: Any, job_id: str) -> str:
    try:
        return asyncio.run(_run_analysis(job_id))

    except ValueError:
        # Permanent errors should not be retried.
        raise

    except Exception as exc:
        # Retry potentially temporary infrastructure/AI failures.
        raise self.retry(
            exc=exc,
            countdown=5 * (2 ** self.request.retries),
        )


async def _run_analysis(job_id: str) -> str:
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
            result = await session.execute(
                select(Job).where(Job.id == UUID(job_id))
            )

            job = result.scalar_one_or_none()

            if job is None:
                raise ValueError(f"Job {job_id} not found")

            if not job.description or not job.description.strip():
                raise ValueError("Job has no description to analyze")

            client = AIClient()
            analyzer = JobAnalyzer(client)
            repository = JobAnalysisRepository(session)

            service = JobAnalysisService(
                analyzer=analyzer,
                repository=repository,
            )

            await service.analyze_job(
                job_id=job.id,
                job_description=job.description,
            )

            return job_id

    finally:
        await engine.dispose()