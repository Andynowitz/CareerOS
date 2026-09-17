from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db_session
from app.repositories.job import JobRepository
from app.repositories.job_activity import JobActivityRepository
from app.schemas.application_insights import (
    ApplicationInsightsResponse,
)
from app.schemas.user import CurrentUserResponse
from app.services.application_insights import (
    ApplicationInsightsService,
)


router = APIRouter(
    prefix="/application-insights",
    tags=["application-insights"],
)


@router.get(
    "",
    response_model=ApplicationInsightsResponse,
)
async def get_application_insights(
    current_user: CurrentUserResponse = Depends(
        get_current_user,
    ),
    session: AsyncSession = Depends(get_db_session),
) -> ApplicationInsightsResponse:
    job_repository = JobRepository(session)
    activity_repository = JobActivityRepository(session)

    jobs = await job_repository.get_all(
        current_user.id,
    )

    activities = await activity_repository.get_all_for_user(
        current_user.id,
    )

    insights = ApplicationInsightsService.calculate(
        jobs,
        activities,
    )

    return ApplicationInsightsResponse.model_validate(
        insights,
    )