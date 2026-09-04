from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.job_activities import router as job_activities_router
from app.api.v1.endpoints.jobs import router as jobs_router
from app.db.session import get_db_session


router = APIRouter(prefix="/api/v1")

router.include_router(health_router)
router.include_router(auth_router)
router.include_router(jobs_router)
router.include_router(job_activities_router)


@router.get("/db-check", tags=["system"])
async def database_check(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    return {"status": "ok"}