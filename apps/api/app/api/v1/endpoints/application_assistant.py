from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db_session
from app.repositories.job import JobRepository
from app.repositories.job_activity import JobActivityRepository
from app.schemas.application_assistant import (
    ApplicationAssistantResponse,
)
from app.schemas.user import CurrentUserResponse
from app.services.application_assistant import (
    ApplicationAssistantService,
)


router = APIRouter(
    prefix="/jobs",
    tags=["application-assistant"],
)


@router.get(
    "/{job_id}/assistant",
    response_model=ApplicationAssistantResponse,
)
async def get_application_assistant(
    job_id: UUID,
    current_user: CurrentUserResponse = Depends(
        get_current_user,
    ),
    session: AsyncSession = Depends(get_db_session),
) -> ApplicationAssistantResponse:
    job_repository = JobRepository(session)
    activity_repository = JobActivityRepository(session)

    job = await job_repository.get_by_id(
        job_id,
        current_user.id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    activities = await activity_repository.get_all(
        job_id,
        current_user.id,
    )

    assistant = ApplicationAssistantService.build(
        job,
        activities,
    )

    return ApplicationAssistantResponse.model_validate(
        assistant,
    )