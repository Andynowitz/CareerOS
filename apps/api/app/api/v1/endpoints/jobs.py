from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db_session
from app.models.job import Job
from app.models.job_activity import JobActivity, JobActivityType
from app.repositories.job import JobRepository
from app.repositories.job_activity import JobActivityRepository
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.schemas.user import CurrentUserResponse
from app.repositories.job_analysis import JobAnalysisRepository
from app.schemas.job_analysis import JobAnalysisResponse
from app.schemas.analysis_task import AnalysisTaskResponse
from app.tasks.job_analysis import analyze_job_task
from celery.result import AsyncResult
from app.tasks.celery_app import celery_app
from sqlalchemy import select
from app.models.resume import Resume
from app.repositories.resume_analysis import ResumeAnalysisRepository
from app.schemas.job_insight import JobInsightResponse
from app.tasks.job_insight import analyze_job_insight_task
from app.repositories.job_insight import JobInsightRepository


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

    job_repository = JobRepository(session)

    created_job = await job_repository.create(job)

    # Automatically record job creation.
    activity = JobActivity(
        job_id=created_job.id,
        user_id=current_user.id,
        type=JobActivityType.CREATED,
        description="Job application created.",
    )

    activity_repository = JobActivityRepository(session)

    await activity_repository.create(activity)

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

    return [
        JobResponse.model_validate(job)
        for job in jobs
    ]


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

    # Remember the old status before applying the update.
    old_status = job.status

    update_data = job_data.model_dump(
        exclude_unset=True,
    )

    if "url" in update_data:
        update_data["url"] = (
            str(update_data["url"])
            if update_data["url"] is not None
            else None
        )

    for field, value in update_data.items():
        setattr(job, field, value)

    updated_job = await job_repository.update(job)

    # Automatically record status changes.
    if (
        "status" in update_data
        and old_status != updated_job.status
    ):
        activity = JobActivity(
            job_id=updated_job.id,
            user_id=current_user.id,
            type=JobActivityType.STATUS_CHANGED,
            old_status=old_status.value,
            new_status=updated_job.status.value,
            description=(
                f"Status changed from "
                f"{old_status.value} to "
                f"{updated_job.status.value}."
            ),
        )

        activity_repository = JobActivityRepository(session)

        await activity_repository.create(activity)

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



@router.post(
    "/{job_id}/analysis",
    response_model=AnalysisTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def analyze_job(
    job_id: UUID,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> AnalysisTaskResponse:
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

    if not job.description or not job.description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job has no description to analyze",
        )

    task = analyze_job_task.delay(str(job.id))

    return AnalysisTaskResponse(
        task_id=task.id,
        status="queued",
    )

@router.get(
    "/{job_id}/analysis/status/{task_id}",
    response_model=AnalysisTaskResponse,
)
async def get_analysis_status(
    job_id: UUID,
    task_id: str,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> AnalysisTaskResponse:
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

    task = AsyncResult(task_id, app=celery_app)

    return AnalysisTaskResponse(
        task_id=task_id,
        status=task.status,
    )


@router.get(
    "/{job_id}/analysis",
    response_model=JobAnalysisResponse,
)
async def get_job_analysis(
    job_id: UUID,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> JobAnalysisResponse:
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

    repository = JobAnalysisRepository(session)

    analysis = await repository.get_latest_for_job(job.id)

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis found for this job",
        )

    return JobAnalysisResponse.model_validate(analysis)


@router.get(
    "/{job_id}/analysis/history",
    response_model=list[JobAnalysisResponse],
)
async def get_job_analysis_history(
    job_id: UUID,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[JobAnalysisResponse]:
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

    repository = JobAnalysisRepository(session)

    analyses = await repository.get_history_for_job(job.id)

    return [
        JobAnalysisResponse.model_validate(analysis)
        for analysis in analyses
    ]


@router.post(
    "/{job_id}/insights/{resume_id}",
    response_model=AnalysisTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def analyze_job_insight(
    job_id: UUID,
    resume_id: UUID,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> AnalysisTaskResponse:
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

    resume_result = await session.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
    )

    resume = resume_result.scalar_one_or_none()

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    job_analysis_repository = JobAnalysisRepository(session)

    job_analysis = await job_analysis_repository.get_latest_for_job(
        job.id,
    )

    if job_analysis is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job must be analyzed before generating insights",
        )

    resume_analysis_repository = ResumeAnalysisRepository(session)

    resume_analysis = await resume_analysis_repository.get_latest_for_resume(
        resume.id,
    )

    if resume_analysis is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume must be analyzed before generating insights",
        )

    task = analyze_job_insight_task.delay(
        str(job.id),
        str(resume.id),
    )

    return AnalysisTaskResponse(
        task_id=task.id,
        status="queued",
    )


@router.get(
    "/{job_id}/insights/{resume_id}",
    response_model=JobInsightResponse,
)
async def get_job_insight(
    job_id: UUID,
    resume_id: UUID,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> JobInsightResponse:
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

    result = await session.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
    )

    resume = result.scalar_one_or_none()

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    repository = JobInsightRepository(session)

    insight = await repository.get_latest_for_job_and_resume(
        job.id,
        resume.id,
    )

    if insight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job insight not found",
        )

    return JobInsightResponse.model_validate(insight)


@router.get(
    "/{job_id}/insights/{resume_id}/history",
    response_model=list[JobInsightResponse],
)
async def get_job_insight_history(
    job_id: UUID,
    resume_id: UUID,
    current_user: CurrentUserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[JobInsightResponse]:
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

    result = await session.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
    )

    resume = result.scalar_one_or_none()

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    repository = JobInsightRepository(session)

    insights = await repository.get_history_for_job_and_resume(
        job.id,
        resume.id,
    )

    return [
        JobInsightResponse.model_validate(insight)
        for insight in insights
    ]
