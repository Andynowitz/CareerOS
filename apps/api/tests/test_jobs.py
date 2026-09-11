from httpx import AsyncClient


async def create_job(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/v1/jobs",
        json={
            "title": "Software Engineer",
            "company": "Test Company",
            "location": "Vienna",
            "url": "https://example.com",
            "description": "Test job",
            "status": "saved",
        },
    )

    assert response.status_code == 201
    return response.json()


async def test_create_job(client: AsyncClient) -> None:
    job = await create_job(client)

    assert job["title"] == "Software Engineer"
    assert job["company"] == "Test Company"
    assert job["status"] == "saved"
    assert "id" in job


async def test_get_jobs(client: AsyncClient) -> None:
    await create_job(client)

    response = await client.get("/api/v1/jobs")

    assert response.status_code == 200

    jobs = response.json()

    assert isinstance(jobs, list)
    assert len(jobs) >= 1


async def test_get_job(client: AsyncClient) -> None:
    job = await create_job(client)

    response = await client.get(
        f"/api/v1/jobs/{job['id']}"
    )

    assert response.status_code == 200

    result = response.json()

    assert result["id"] == job["id"]
    assert result["title"] == "Software Engineer"


async def test_update_job(client: AsyncClient) -> None:
    job = await create_job(client)

    response = await client.patch(
        f"/api/v1/jobs/{job['id']}",
        json={
            "title": "Senior Software Engineer",
        },
    )

    assert response.status_code == 200

    updated_job = response.json()

    assert updated_job["title"] == "Senior Software Engineer"


async def test_change_job_status(client: AsyncClient) -> None:
    job = await create_job(client)

    response = await client.patch(
        f"/api/v1/jobs/{job['id']}",
        json={
            "status": "interview",
        },
    )

    assert response.status_code == 200

    updated_job = response.json()

    assert updated_job["status"] == "interview"


async def test_status_change_creates_activity(
    client: AsyncClient,
) -> None:
    job = await create_job(client)

    response = await client.patch(
        f"/api/v1/jobs/{job['id']}",
        json={
            "status": "applied",
        },
    )

    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/jobs/{job['id']}/activities"
    )

    assert response.status_code == 200

    activities = response.json()

    status_activities = [
        activity
        for activity in activities
        if activity["type"] == "status_changed"
    ]

    assert len(status_activities) >= 1

    activity = status_activities[0]

    assert activity["old_status"] == "saved"
    assert activity["new_status"] == "applied"


async def test_delete_job(client: AsyncClient) -> None:
    job = await create_job(client)

    response = await client.delete(
        f"/api/v1/jobs/{job['id']}"
    )

    assert response.status_code == 204

    response = await client.get(
        f"/api/v1/jobs/{job['id']}"
    )

    assert response.status_code == 404