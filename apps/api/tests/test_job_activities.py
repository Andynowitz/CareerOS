from httpx import AsyncClient


async def create_job(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/v1/jobs",
        json={
            "title": "Backend Developer",
            "company": "Activity Test Company",
            "location": "Vienna",
            "status": "saved",
        },
    )

    assert response.status_code == 201

    return response.json()


async def test_job_creation_creates_activity(
    client: AsyncClient,
) -> None:
    job = await create_job(client)

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/activities"
    )

    assert response.status_code == 200

    activities = response.json()

    created_activities = [
        activity
        for activity in activities
        if activity["type"] == "created"
    ]

    assert len(created_activities) == 1

    activity = created_activities[0]

    assert activity["job_id"] == job["id"]
    assert activity["description"] == "Job application created."


async def test_create_manual_activity(
    client: AsyncClient,
) -> None:
    job = await create_job(client)

    response = await client.post(
        f"/api/v1/jobs/{job['id']}/activities",
        json={
            "type": "note",
            "description": "Called the company.",
        },
    )

    assert response.status_code == 201

    activity = response.json()

    assert activity["job_id"] == job["id"]
    assert activity["type"] == "note"
    assert activity["description"] == "Called the company."


async def test_get_job_activities(
    client: AsyncClient,
) -> None:
    job = await create_job(client)

    await client.post(
        f"/api/v1/jobs/{job['id']}/activities",
        json={
            "type": "email",
            "description": "Sent application follow-up.",
        },
    )

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/activities"
    )

    assert response.status_code == 200

    activities = response.json()

    assert len(activities) >= 2

    types = [activity["type"] for activity in activities]

    assert "created" in types
    assert "email" in types


async def test_activity_belongs_to_correct_job(
    client: AsyncClient,
) -> None:
    job = await create_job(client)

    response = await client.post(
        f"/api/v1/jobs/{job['id']}/activities",
        json={
            "type": "interview",
            "description": "First technical interview.",
        },
    )

    assert response.status_code == 201

    activity = response.json()

    assert activity["job_id"] == job["id"]