from unittest.mock import MagicMock

from httpx import AsyncClient

from datetime import datetime, timezone
from uuid import uuid4

from app.models.job_analysis import JobAnalysis
from app.models.job_insight import JobInsight
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis

async def create_job_with_description(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/v1/jobs",
        json={
            "title": "Python Developer",
            "company": "AI Company",
            "location": "Vienna",
            "description": (
                "We are looking for a Python developer with "
                "FastAPI and Docker experience."
            ),
            "status": "saved",
        },
    )

    assert response.status_code == 201
    return response.json()


async def create_job_without_description(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/v1/jobs",
        json={
            "title": "Python Developer",
            "company": "AI Company",
            "location": "Vienna",
            "status": "saved",
        },
    )

    assert response.status_code == 201
    return response.json()


async def test_start_job_analysis(
    client: AsyncClient,
    monkeypatch,
) -> None:
    job = await create_job_with_description(client)

    mock_task = MagicMock()
    mock_task.id = "test-task-id"

    monkeypatch.setattr(
        "app.tasks.job_analysis.analyze_job_task.delay",
        lambda job_id: mock_task,
    )

    response = await client.post(
        f"/api/v1/jobs/{job['id']}/analysis"
    )

    assert response.status_code == 202

    result = response.json()

    assert result["task_id"] == "test-task-id"
    assert result["status"] == "queued"


async def test_start_job_analysis_without_description(
    client: AsyncClient,
) -> None:
    job = await create_job_without_description(client)

    response = await client.post(
        f"/api/v1/jobs/{job['id']}/analysis"
    )

    assert response.status_code == 400

    result = response.json()

    assert result["detail"] == "Job has no description to analyze"


async def test_start_job_analysis_for_unknown_job(
    client: AsyncClient,
    monkeypatch,
) -> None:
    mock_task = MagicMock()
    mock_task.id = "test-task-id"

    monkeypatch.setattr(
        "app.tasks.job_analysis.analyze_job_task.delay",
        lambda job_id: mock_task,
    )

    response = await client.post(
        "/api/v1/jobs/00000000-0000-0000-0000-000000000000/analysis"
    )

    assert response.status_code == 404

    result = response.json()

    assert result["detail"] == "Job not found"


async def test_get_analysis_status(
    client: AsyncClient,
    monkeypatch,
) -> None:
    job = await create_job_with_description(client)

    class MockTask:
        status = "SUCCESS"

    monkeypatch.setattr(
        "app.api.v1.endpoints.jobs.AsyncResult",
        lambda task_id, app: MockTask(),
    )

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/analysis/status/test-task-id"
    )

    assert response.status_code == 200

    result = response.json()

    assert result["task_id"] == "test-task-id"
    assert result["status"] == "SUCCESS"


async def test_get_latest_job_analysis(
    client: AsyncClient,
) -> None:
    job = await create_job_with_description(client)

    analysis = JobAnalysis(
        job_id=job["id"],
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker"],
        responsibilities=["Develop backend services"],
        experience_requirements="2+ years",
        education_requirements="Bachelor's degree",
        keywords=["Python", "FastAPI", "Docker"],
        salary_information={
            "min": 3000,
            "max": 4500,
        },
        raw_analysis={
            "required_skills": ["Python", "FastAPI"],
        },
    )

    # We need the database session used by the test fixtures.
    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        session.add(analysis)
        await session.commit()
        await session.refresh(analysis)

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/analysis"
    )

    assert response.status_code == 200

    result = response.json()

    assert result["job_id"] == job["id"]
    assert result["required_skills"] == ["Python", "FastAPI"]
    assert result["preferred_skills"] == ["Docker"]
    assert result["responsibilities"] == ["Develop backend services"]
    assert result["experience_requirements"] == "2+ years"
    assert result["education_requirements"] == "Bachelor's degree"
    assert result["keywords"] == ["Python", "FastAPI", "Docker"]


async def test_get_latest_job_analysis_when_none_exists(
    client: AsyncClient,
) -> None:
    job = await create_job_with_description(client)

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/analysis"
    )

    assert response.status_code == 404

    result = response.json()

    assert result["detail"] == "Job analysis not found"


async def test_get_job_analysis_history(
    client: AsyncClient,
) -> None:
    job = await create_job_with_description(client)

    first_analysis = JobAnalysis(
        job_id=job["id"],
        required_skills=["Python"],
        preferred_skills=[],
        responsibilities=["Build APIs"],
        experience_requirements=None,
        education_requirements=None,
        keywords=["Python"],
        salary_information=None,
        raw_analysis=None,
    )

    second_analysis = JobAnalysis(
        job_id=job["id"],
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker"],
        responsibilities=["Build APIs", "Maintain services"],
        experience_requirements="2+ years",
        education_requirements="Bachelor's degree",
        keywords=["Python", "FastAPI", "Docker"],
        salary_information=None,
        raw_analysis=None,
    )

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        session.add(first_analysis)
        await session.commit()

        session.add(second_analysis)
        await session.commit()

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/analysis/history"
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 2

    # History should be newest first.
    assert history[0]["id"] == str(second_analysis.id)
    assert history[1]["id"] == str(first_analysis.id)



async def test_start_job_insight(
    client: AsyncClient,
    monkeypatch,
):
    job = await create_job_with_description(client)

    resume_id = uuid4()

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id",
            name="Test Resume",
        )
        session.add(resume)

        job_analysis = JobAnalysis(
            job_id=job["id"],
            required_skills=["Python", "FastAPI"],
            preferred_skills=["Docker"],
            responsibilities=["Develop backend services"],
            experience_requirements="2+ years",
            education_requirements="Bachelor's degree",
            keywords=["Python", "FastAPI"],
            salary_information=None,
            raw_analysis={},
        )
        session.add(job_analysis)

        resume_analysis = ResumeAnalysis(
            resume_id=resume_id,
            skills=["Python", "FastAPI"],
            experience_summary="Backend development experience",
            education_summary="Bachelor's degree",
            projects_summary="Backend projects",
            raw_analysis={},
        )
        session.add(resume_analysis)

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


async def test_get_latest_job_insight(client: AsyncClient):
    job = await create_job_with_description(client)
    resume_id = uuid4()

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id",
            name="Test Resume",
        )

        insight = JobInsight(
            job_id=job["id"],
            resume_id=resume_id,
            match_score=85,
            matching_skills=["Python", "FastAPI"],
            missing_skills=["Kubernetes"],
            strengths=["Strong backend experience"],
            weaknesses=["Limited Kubernetes experience"],
            recommendations=["Learn Kubernetes"],
            overall_assessment="Strong candidate.",
            raw_insight={"match_score": 85},
        )

        session.add(resume)
        await session.flush()

        session.add(insight)
        await session.commit()

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}"
    )

    assert response.status_code == 200

    result = response.json()

    assert result["job_id"] == job["id"]
    assert result["resume_id"] == str(resume_id)
    assert result["match_score"] == 85
    assert result["matching_skills"] == ["Python", "FastAPI"]
    assert result["missing_skills"] == ["Kubernetes"]
    assert result["strengths"] == ["Strong backend experience"]
    assert result["weaknesses"] == ["Limited Kubernetes experience"]
    assert result["recommendations"] == ["Learn Kubernetes"]
    assert result["overall_assessment"] == "Strong candidate."


async def test_get_job_insight_history(client: AsyncClient):
    job = await create_job_with_description(client)
    resume_id = uuid4()

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id",
            name="Test Resume",
        )
        session.add(resume)
        await session.flush()

        insight_1 = JobInsight(
            job_id=job["id"],
            resume_id=resume_id,
            match_score=70,
            matching_skills=["Python"],
            missing_skills=["Docker"],
            strengths=["Backend experience"],
            weaknesses=["Limited Docker"],
            recommendations=["Learn Docker"],
            overall_assessment="Good candidate.",
            raw_insight={"match_score": 70},
            created_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        )

        insight_2 = JobInsight(
            job_id=job["id"],
            resume_id=resume_id,
            match_score=85,
            matching_skills=["Python", "FastAPI"],
            missing_skills=["Kubernetes"],
            strengths=["Strong backend experience"],
            weaknesses=["Limited Kubernetes"],
            recommendations=["Learn Kubernetes"],
            overall_assessment="Strong candidate.",
            raw_insight={"match_score": 85},
            created_at=datetime(2026, 1, 2, 12, 0, tzinfo=timezone.utc),
        )

        session.add_all([insight_1, insight_2])
        await session.commit()

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}/history"
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result) == 2
    assert result[0]["match_score"] == 85
    assert result[1]["match_score"] == 70


async def test_start_resume_analysis_without_extracted_text(
    client: AsyncClient,
    monkeypatch,
):
    resume_id = uuid4()

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id",
            name="Test Resume",
            current_version=1,
        )
        session.add(resume)
        await session.commit()

    response = await client.post(
        f"/api/v1/resumes/{resume_id}/analysis"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Resume has no extracted text to analyze"


async def test_start_job_insight_without_job_analysis(client: AsyncClient):
    job = await create_job_with_description(client)
    resume_id = uuid4()

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id",
            name="Test Resume",
        )
        session.add(resume)
        await session.commit()

    response = await client.post(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Job must be analyzed before generating insights"
    )


async def test_start_job_insight_without_resume_analysis(client: AsyncClient):
    job = await create_job_with_description(client)
    resume_id = uuid4()

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id",
            name="Test Resume",
        )
        session.add(resume)
        await session.flush()

        job_analysis = JobAnalysis(
            job_id=job["id"],
            required_skills=["Python", "FastAPI"],
            preferred_skills=["Docker"],
            responsibilities=["Develop backend services"],
            experience_requirements="2+ years",
            education_requirements="Bachelor's degree",
            keywords=["Python", "FastAPI"],
            salary_information=None,
            raw_analysis={},
        )
        session.add(job_analysis)
        await session.commit()

    response = await client.post(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Resume must be analyzed before generating insights"
    )


async def test_start_job_analysis_not_found(client: AsyncClient):
    job_id = uuid4()

    response = await client.post(
        f"/api/v1/jobs/{job_id}/analysis"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

async def test_start_job_insight_resume_not_found(client: AsyncClient):
    job = await create_job_with_description(client)
    resume_id = uuid4()

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        job_analysis = JobAnalysis(
            job_id=job["id"],
            required_skills=["Python"],
            preferred_skills=[],
            responsibilities=["Develop software"],
            experience_requirements=None,
            education_requirements=None,
            keywords=["Python"],
            salary_information=None,
            raw_analysis={},
        )
        session.add(job_analysis)
        await session.commit()

    response = await client.post(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume not found"


async def test_start_job_insight_resume_belongs_to_other_user(
    client: AsyncClient,
    as_second_user,
):
    job = await create_job_with_description(client)

    resume_id = uuid4()

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id-2",
            name="Other User Resume",
        )
        session.add(resume)
        await session.commit()

    response = await client.post(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume not found"


async def test_get_job_insight_resume_belongs_to_other_user(
    client: AsyncClient,
):
    job = await create_job_with_description(client)
    resume_id = uuid4()

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id-2",
            name="Other User Resume",
        )
        session.add(resume)
        await session.flush()

        insight = JobInsight(
            job_id=job["id"],
            resume_id=resume_id,
            match_score=90,
            matching_skills=["Python"],
            missing_skills=[],
            strengths=["Strong candidate"],
            weaknesses=[],
            recommendations=[],
            overall_assessment="Excellent candidate.",
            raw_insight={"match_score": 90},
        )
        session.add(insight)
        await session.commit()

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume not found"


async def test_get_job_insight_history_resume_belongs_to_other_user(
    client: AsyncClient,
):
    job = await create_job_with_description(client)
    resume_id = uuid4()

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id-2",
            name="Other User Resume",
        )
        session.add(resume)
        await session.flush()

        insight = JobInsight(
            job_id=job["id"],
            resume_id=resume_id,
            match_score=90,
            matching_skills=["Python"],
            missing_skills=[],
            strengths=["Strong candidate"],
            weaknesses=[],
            recommendations=[],
            overall_assessment="Excellent candidate.",
            raw_insight={"match_score": 90},
        )
        session.add(insight)
        await session.commit()

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}/history"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume not found"


async def test_get_job_insight_not_found(client: AsyncClient):
    job = await create_job_with_description(client)
    resume_id = uuid4()

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id",
            name="Test Resume",
        )
        session.add(resume)
        await session.commit()

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job insight not found"


async def test_get_job_insight_history_empty(client: AsyncClient):
    job = await create_job_with_description(client)
    resume_id = uuid4()

    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id",
            name="Test Resume",
        )
        session.add(resume)
        await session.commit()

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}/history"
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_get_job_insight_resume_not_found(client: AsyncClient):
    job = await create_job_with_description(client)
    resume_id = uuid4()

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/insights/{resume_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume not found"


