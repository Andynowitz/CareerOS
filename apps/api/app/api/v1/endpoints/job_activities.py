from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db_session
from app.models.job_activity import JobActivity
from app.repositories.job import JobRepository
from app.repositories.job_activity import JobActivityRepository
from app.schemas.job_activity import (
    JobActivityCreate,
    JobActivityResponse,
)
from app.schemas.user import CurrentUserResponse


router = APIRouter(
    prefix="/jobs/{job_id}/activities",
    tags=["job activities"],
)


@router.get(
    "",
    response_model=list[JobActivityResponse],
)
async def get_job_activities(
    job_id: UUID,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[JobActivityResponse]:
    job_repository = JobRepository(session)

    job = await job_repository.get_by_id(
        job_id,
        current_user.id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    repository = JobActivityRepository(session)

    activities = await repository.get_all(
        job_id,
        current_user.id,
    )

    return [
        JobActivityResponse.model_validate(activity)
        for activity in activities
    ]


@router.post(
    "",
    response_model=JobActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job_activity(
    job_id: UUID,
    activity_data: JobActivityCreate,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> JobActivityResponse:
    job_repository = JobRepository(session)

    job = await job_repository.get_by_id(
        job_id,
        current_user.id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    activity = JobActivity(
        job_id=job_id,
        user_id=current_user.id,
        type=activity_data.type,
        description=activity_data.description,
    )

    repository = JobActivityRepository(session)

    created_activity = await repository.create(activity)

    return JobActivityResponse.model_validate(created_activity)