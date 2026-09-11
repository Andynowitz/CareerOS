from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JobInsight(Base):
    __tablename__ = "job_insight"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    match_score: Mapped[int] = mapped_column(
        nullable=False,
    )

    matching_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    missing_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    strengths: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    weaknesses: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    recommendations: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    overall_assessment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    raw_insight: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


async def test_start_job_insight(
    client: AsyncClient,
    monkeypatch,
) -> None:
    job = await create_job_with_description(client)

    from tests.conftest import TestingSessionLocal

    resume_id = uuid4()

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user",
            name="Test Resume",
            current_version=1,
        )
        session.add(resume)
        await session.commit()

    job_analysis = JobAnalysis(
        job_id=job["id"],
        required_skills=["Python"],
        preferred_skills=["Docker"],
        responsibilities=["Build APIs"],
        experience_requirements=None,
        education_requirements=None,
        keywords=["Python"],
        salary_information=None,
        raw_analysis={"required_skills": ["Python"]},
    )

    async with TestingSessionLocal() as session:
        session.add(job_analysis)
        await session.commit()

    mock_task = MagicMock()
    mock_task.id = "test-insight-task-id"

    monkeypatch.setattr(
        "app.tasks.job_insight.analyze_job_insight_task.delay",
        lambda job_id, resume_id: mock_task,
    )

    response = await client.post(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}"
    )

    assert response.status_code == 202

    result = response.json()

    assert result["task_id"] == "test-insight-task-id"
    assert result["status"] == "queued"



async def test_start_job_insight(
    client: AsyncClient,
    monkeypatch,
):
    job = await create_job_with_description(client)

    resume_id = uuid4()

    # Create a resume belonging to the test user.
    from app.db.session import get_db_session
    from app.tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id",
            name="Test Resume",
        )
        session.add(resume)
        await session.commit()

    mock_task = MagicMock()
    mock_task.id = "test-insight-task-id"

    monkeypatch.setattr(
        "app.tasks.job_insight.analyze_job_insight_task.delay",
        lambda job_id, resume_id: mock_task,
    )

    response = await client.post(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}"
    )

    assert response.status_code == 202

    result = response.json()

    assert result["task_id"] == "test-insight-task-id"
    assert result["status"] == "queued"

