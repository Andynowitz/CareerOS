from httpx import AsyncClient


async def create_job(
    client: AsyncClient,
    title: str,
    status: str,
) -> dict:
    response = await client.post(
        "/api/v1/jobs",
        json={
            "title": title,
            "company": "Application Insights Test Company",
            "location": "Vienna",
            "description": "Application insights test job",
            "status": status,
        },
    )

    assert response.status_code == 201
    return response.json()


async def get_insights(
    client: AsyncClient,
) -> dict:
    response = await client.get(
        "/api/v1/application-insights"
    )

    assert response.status_code == 200
    return response.json()


async def test_application_insights_funnel(
    client: AsyncClient,
) -> None:
    jobs_before = await client.get("/api/v1/jobs")
    assert jobs_before.status_code == 200

    before_count = len(jobs_before.json())

    await create_job(client, "Saved Job", "saved")
    await create_job(client, "Applied Job", "applied")
    await create_job(client, "Interview Job", "interview")
    await create_job(client, "Offer Job", "offer")
    await create_job(client, "Rejected Job", "rejected")
    await create_job(client, "Withdrawn Job", "withdrawn")

    data = await get_insights(client)

    assert data["total_applications"] == before_count + 6

    assert data["funnel"]["saved"] >= 1
    assert data["funnel"]["applied"] >= 1
    assert data["funnel"]["interview"] >= 1
    assert data["funnel"]["offer"] >= 1
    assert data["funnel"]["rejected"] >= 1
    assert data["funnel"]["withdrawn"] >= 1


async def test_application_insights_rates(
    client: AsyncClient,
) -> None:
    jobs_before = await client.get("/api/v1/jobs")
    assert jobs_before.status_code == 200

    before_jobs = jobs_before.json()

    before_applied = sum(
        1
        for job in before_jobs
        if job["status"]
        in {
            "applied",
            "interview",
            "offer",
            "rejected",
            "withdrawn",
        }
    )

    before_interviews = sum(
        1
        for job in before_jobs
        if job["status"]
        in {
            "interview",
            "offer",
        }
    )

    before_offers = sum(
        1
        for job in before_jobs
        if job["status"] == "offer"
    )

    before_responses = sum(
        1
        for job in before_jobs
        if job["status"]
        in {
            "interview",
            "offer",
            "rejected",
            "withdrawn",
        }
    )

    await create_job(client, "Applied 1", "applied")
    await create_job(client, "Applied 2", "applied")
    await create_job(client, "Interview", "interview")
    await create_job(client, "Offer", "offer")
    await create_job(client, "Rejected", "rejected")

    data = await get_insights(client)

    assert data["applied"] == before_applied + 5
    assert data["interviews"] == before_interviews + 2
    assert data["offers"] == before_offers + 1
    assert data["response_count"] == before_responses + 3

    expected_response_rate = (
        (before_responses + 3)
        / (before_applied + 5)
        * 100
    )

    expected_interview_rate = (
        (before_interviews + 2)
        / (before_applied + 5)
        * 100
    )

    expected_offer_rate = (
        (before_offers + 1)
        / (before_applied + 5)
        * 100
    )

    assert data["response_rate"] == round(
        expected_response_rate,
        2,
    )

    assert data["interview_rate"] == round(
        expected_interview_rate,
        2,
    )

    assert data["offer_rate"] == round(
        expected_offer_rate,
        2,
    )


async def test_application_insights_status_transitions(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/application-insights"
    )
    assert response.status_code == 200

    before = response.json()["status_transitions"]

    job = await create_job(
        client,
        "Transition Job",
        "saved",
    )

    response = await client.patch(
        f"/api/v1/jobs/{job['id']}",
        json={"status": "applied"},
    )
    assert response.status_code == 200

    response = await client.patch(
        f"/api/v1/jobs/{job['id']}",
        json={"status": "interview"},
    )
    assert response.status_code == 200

    response = await client.patch(
        f"/api/v1/jobs/{job['id']}",
        json={"status": "offer"},
    )
    assert response.status_code == 200

    data = await get_insights(client)

    after = data["status_transitions"]

    assert after["saved->applied"] == (
        before.get("saved->applied", 0) + 1
    )

    assert after["applied->interview"] == (
        before.get("applied->interview", 0) + 1
    )

    assert after["interview->offer"] == (
        before.get("interview->offer", 0) + 1
    )