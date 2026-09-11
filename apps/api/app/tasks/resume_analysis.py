from __future__ import annotations

import asyncio
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.ai.analyzers.resume_analyzer import ResumeAnalyzer
from app.ai.client import AIClient
from app.core.config import get_settings
from app.models.resume import Resume
from app.repositories.resume_analysis import ResumeAnalysisRepository
from app.services.resume_analysis import ResumeAnalysisService
from app.tasks.celery_app import celery_app


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def analyze_resume_task(self, resume_id: str) -> str:
    try:
        return asyncio.run(_run_analysis(resume_id))
    except ValueError:
        raise
    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=5 * (2 ** self.request.retries),
        )


async def _run_analysis(resume_id: str) -> str:
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
                select(Resume)
                .where(Resume.id == UUID(resume_id))
            )
            resume = result.scalar_one_or_none()

            if resume is None:
                raise ValueError(f"Resume {resume_id} not found")

            current_version = next(
                (
                    version
                    for version in resume.versions
                    if version.version == resume.current_version
                ),
                None,
            )

            if (
                current_version is None
                or not current_version.extracted_text
                or not current_version.extracted_text.strip()
            ):
                raise ValueError(
                    "Resume has no extracted text to analyze"
                )

            client = AIClient()
            analyzer = ResumeAnalyzer(client)
            repository = ResumeAnalysisRepository(session)

            service = ResumeAnalysisService(
                analyzer=analyzer,
                repository=repository,
            )

            await service.analyze_resume(
                resume_id=resume.id,
                resume_text=current_version.extracted_text,
            )

            return resume_id

    finally:
        await engine.dispose()