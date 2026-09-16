import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.resume import Resume
from app.repositories.job_match import JobMatchRepository


async def create_parent_records(
    db_session: AsyncSession,
    job_id: uuid.UUID,
    resume_id: uuid.UUID,
) -> None:
    db_session.add_all(
        [
            Job(
                id=job_id,
                user_id="test-user-id",
                title="Software Engineer",
                company="Test Company",
            ),
            Resume(
                id=resume_id,
                user_id="test-user-id",
                name="Test Resume",
            ),
        ]
    )
    await db_session.flush()


@pytest.mark.asyncio
async def test_create_and_get_job_match(
    db_session: AsyncSession,
) -> None:
    repository = JobMatchRepository(db_session)

    job_id = uuid.uuid4()
    resume_id = uuid.uuid4()
    await create_parent_records(db_session, job_id, resume_id)

    match = await repository.create(
        job_id=job_id,
        resume_id=resume_id,
        score=85,
        required_skills_score=0.75,
        preferred_skills_score=1.0,
        experience_score=1.0,
        education_score=1.0,
        keywords_score=0.5,
        matched_required_skills=["c#", ".net"],
        missing_required_skills=["docker"],
        matched_preferred_skills=["git"],
        missing_preferred_skills=[],
        explanations=["Matched 2 of 3 required skills."],
    )

    await db_session.commit()

    assert match.id is not None
    assert match.score == 85

    stored = await repository.get_by_id(match.id)

    assert stored is not None
    assert stored.id == match.id
    assert stored.job_id == job_id
    assert stored.resume_id == resume_id
    assert stored.score == 85
    assert stored.missing_required_skills == ["docker"]


@pytest.mark.asyncio
async def test_get_latest_returns_most_recent_match(
    db_session: AsyncSession,
) -> None:
    repository = JobMatchRepository(db_session)

    job_id = uuid.uuid4()
    resume_id = uuid.uuid4()
    await create_parent_records(db_session, job_id, resume_id)

    first = await repository.create(
        job_id=job_id,
        resume_id=resume_id,
        score=70,
        required_skills_score=0.5,
        preferred_skills_score=1.0,
        experience_score=1.0,
        education_score=1.0,
        keywords_score=1.0,
        matched_required_skills=["c#"],
        missing_required_skills=["docker"],
        matched_preferred_skills=[],
        missing_preferred_skills=[],
        explanations=["First match."],
    )

    await db_session.commit()

    second = await repository.create(
        job_id=job_id,
        resume_id=resume_id,
        score=90,
        required_skills_score=1.0,
        preferred_skills_score=1.0,
        experience_score=1.0,
        education_score=1.0,
        keywords_score=1.0,
        matched_required_skills=["c#", ".net", "docker"],
        missing_required_skills=[],
        matched_preferred_skills=[],
        missing_preferred_skills=[],
        explanations=["Second match."],
    )

    await db_session.commit()

    latest = await repository.get_latest(
        job_id=job_id,
        resume_id=resume_id,
    )

    assert latest is not None
    assert latest.id == second.id
    assert latest.id != first.id
    assert latest.score == 90


@pytest.mark.asyncio
async def test_list_history_returns_matches_newest_first(
    db_session: AsyncSession,
) -> None:
    repository = JobMatchRepository(db_session)

    job_id = uuid.uuid4()
    resume_id = uuid.uuid4()
    await create_parent_records(db_session, job_id, resume_id)

    first = await repository.create(
        job_id=job_id,
        resume_id=resume_id,
        score=60,
        required_skills_score=0.5,
        preferred_skills_score=0.5,
        experience_score=1.0,
        education_score=1.0,
        keywords_score=1.0,
        matched_required_skills=[],
        missing_required_skills=[],
        matched_preferred_skills=[],
        missing_preferred_skills=[],
        explanations=["First match."],
    )

    await db_session.commit()

    second = await repository.create(
        job_id=job_id,
        resume_id=resume_id,
        score=80,
        required_skills_score=0.75,
        preferred_skills_score=1.0,
        experience_score=1.0,
        education_score=1.0,
        keywords_score=1.0,
        matched_required_skills=["c#"],
        missing_required_skills=[],
        matched_preferred_skills=["git"],
        missing_preferred_skills=[],
        explanations=["Second match."],
    )

    await db_session.commit()

    history = await repository.list_history(
        job_id=job_id,
        resume_id=resume_id,
    )

    assert len(history) == 2
    assert history[0].id == second.id
    assert history[1].id == first.id
    