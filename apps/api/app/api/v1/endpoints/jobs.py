from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db_session
from app.models.job import Job
from app.repositories.job import JobRepository
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.schemas.user import CurrentUserResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job(
    job_data: JobCreate,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> JobResponse:
    job = Job(
        user_id=current_user.id,
        title=job_data.title,
        company=job_data.company,
        location=job_data.location,
        url=str(job_data.url) if job_data.url else None,
        description=job_data.description,
        status=job_data.status,
    )

    repository = JobRepository(session)
    created_job = await repository.create(job)

    return JobResponse.model_validate(created_job)

@router.get(
    "",
    response_model=list[JobResponse],
)
async def get_jobs(
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[JobResponse]:
    repository = JobRepository(session)

    jobs = await repository.get_all(current_user.id)

    return [JobResponse.model_validate(job) for job in jobs]


@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
async def get_job(
    job_id: UUID,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> JobResponse:
    repository = JobRepository(session)

    job = await repository.get_by_id(
        job_id,
        current_user.id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return JobResponse.model_validate(job)

@router.patch(
    "/{job_id}",
    response_model=JobResponse,
)
async def update_job(
    job_id: UUID,
    job_data: JobUpdate,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> JobResponse:
    repository = JobRepository(session)

    job = await repository.get_by_id(
        job_id,
        current_user.id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    update_data = job_data.model_dump(exclude_unset=True)

    if "url" in update_data:
        update_data["url"] = (
            str(update_data["url"])
            if update_data["url"] is not None
            else None
        )

    for field, value in update_data.items():
        setattr(job, field, value)

    updated_job = await repository.update(job)

    return JobResponse.model_validate(updated_job)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_job(
    job_id: UUID,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    repository = JobRepository(session)

    job = await repository.get_by_id(
        job_id,
        current_user.id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    await repository.delete(job)