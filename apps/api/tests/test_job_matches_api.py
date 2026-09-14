from __future__ import annotations

from uuid import uuid4

from httpx import AsyncClient

from app.models.job_analysis import JobAnalysis
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis


async def create_job(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/v1/jobs",
        json={
            "title": "Software Engineer",
            "company": "Test Company",
            "location": "Vienna",
            "description": "Backend software engineering position",
            "status": "saved",
        },
    )

    assert response.status_code == 201
    return response.json()


async def create_resume_and_analyses(
    job_id: str,
) -> str:
    from tests.conftest import TestingSessionLocal

    resume_id = uuid4()

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=resume_id,
            user_id="test-user-id",
            name="Test Resume",
        )

        job_analysis = JobAnalysis(
            job_id=job_id,
            required_skills=["Python", "SQL"],
            preferred_skills=["Docker"],
            responsibilities=["Develop backend services"],
            experience_requirements="2+ years Python experience",
            education_requirements="Bachelor's degree",
            keywords=["FastAPI", "backend"],
        )

        resume_analysis = ResumeAnalysis(
            resume_id=resume_id,
            skills=["Python", "SQL", "Docker"],
            experience_summary="3 years of Python backend development",
            education_summary="Bachelor's degree in Software Engineering",
            projects_summary="Built FastAPI backend applications",
        )

        session.add(resume)
        session.add(job_analysis)
        session.add(resume_analysis)

        await session.commit()

    return str(resume_id)


async def test_create_job_match(
    client: AsyncClient,
) -> None:
    job = await create_job(client)

    resume_id = await create_resume_and_analyses(
        job["id"],
    )

    response = await client.post(
        f"/api/v1/jobs/{job['id']}/matches",
        json={"resume_id": resume_id},
    )

    assert response.status_code == 201, response.text

    body = response.json()

    assert body["job_id"] == job["id"]
    assert body["resume_id"] == resume_id
    assert 0 <= body["score"] <= 100

    assert body["matched_required_skills"] == [
        "python",
        "sql",
    ]
    assert body["missing_required_skills"] == []

    assert body["matched_preferred_skills"] == [
        "docker",
    ]
    assert body["missing_preferred_skills"] == []

    assert "required_skills_score" in body
    assert "preferred_skills_score" in body
    assert "experience_score" in body
    assert "education_score" in body
    assert "keywords_score" in body
    assert isinstance(body["explanations"], list)


async def test_get_latest_job_match(
    client: AsyncClient,
) -> None:
    job = await create_job(client)

    resume_id = await create_resume_and_analyses(
        job["id"],
    )

    create_response = await client.post(
        f"/api/v1/jobs/{job['id']}/matches",
        json={"resume_id": resume_id},
    )

    assert create_response.status_code == 201

    created = create_response.json()

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/matches/latest",
        params={"resume_id": resume_id},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == created["id"]
    assert body["job_id"] == job["id"]
    assert body["resume_id"] == resume_id
    assert body["score"] == created["score"]


async def test_get_job_match_history(
    client: AsyncClient,
) -> None:
    job = await create_job(client)

    resume_id = await create_resume_and_analyses(
        job["id"],
    )

    first_response = await client.post(
        f"/api/v1/jobs/{job['id']}/matches",
        json={"resume_id": resume_id},
    )

    second_response = await client.post(
        f"/api/v1/jobs/{job['id']}/matches",
        json={"resume_id": resume_id},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/matches/history",
        params={"resume_id": resume_id},
    )

    assert response.status_code == 200

    body = response.json()

    assert "matches" in body
    assert len(body["matches"]) == 2

    assert body["matches"][0]["id"] == second_response.json()["id"]
    assert body["matches"][1]["id"] == first_response.json()["id"]


async def test_create_job_match_rejects_other_users_resume(
    client: AsyncClient,
) -> None:
    job = await create_job(client)

    from tests.conftest import TestingSessionLocal

    other_resume_id = uuid4()

    async with TestingSessionLocal() as session:
        resume = Resume(
            id=other_resume_id,
            user_id="test-user-id-2",
            name="Other Resume",
        )

        session.add(resume)
        await session.commit()

    response = await client.post(
        f"/api/v1/jobs/{job['id']}/matches",
        json={"resume_id": str(other_resume_id)},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume not found"


async def test_get_latest_job_match_when_none_exists(
    client: AsyncClient,
) -> None:
    job = await create_job(client)

    resume_id = await create_resume_and_analyses(
        job["id"],
    )

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/matches/latest",
        params={"resume_id": resume_id},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job match not found"