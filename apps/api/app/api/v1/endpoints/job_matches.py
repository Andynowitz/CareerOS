from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db_session
from app.matching.matcher import MatchingEngine
from app.matching.models import JobMatchInput, ResumeMatchInput
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.repositories.job_match import JobMatchRepository
from app.schemas.job_match import (
    JobMatchCreateRequest,
    JobMatchHistoryResponse,
    JobMatchResponse,
)
from app.schemas.user import CurrentUserResponse

router = APIRouter(prefix="/jobs", tags=["job-matches"])


@router.post(
    "/{job_id}/matches",
    response_model=JobMatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a job match",
    description=(
        "Calculate a deterministic match between a job and a resume "
        "using the latest job and resume analyses, then persist the result."
    ),
)
async def create_job_match(
    job_id: UUID,
    request: JobMatchCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUserResponse = Depends(get_current_user),
) -> JobMatchResponse:
    job = await session.get(Job, job_id)

    if job is None or job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    resume = await session.get(Resume, request.resume_id)

    if resume is None or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    job_analysis_result = await session.execute(
        select(JobAnalysis)
        .where(JobAnalysis.job_id == job_id)
        .order_by(JobAnalysis.created_at.desc())
        .limit(1)
    )

    job_analysis = job_analysis_result.scalar_one_or_none()

    if job_analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found",
        )

    resume_analysis_result = await session.execute(
        select(ResumeAnalysis)
        .where(ResumeAnalysis.resume_id == request.resume_id)
        .order_by(ResumeAnalysis.created_at.desc())
        .limit(1)
    )

    resume_analysis = resume_analysis_result.scalar_one_or_none()

    if resume_analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume analysis not found",
        )

    job_input = JobMatchInput(
        required_skills=tuple(job_analysis.required_skills or []),
        preferred_skills=tuple(job_analysis.preferred_skills or []),
        experience_requirements=job_analysis.experience_requirements,
        education_requirements=job_analysis.education_requirements,
        keywords=tuple(job_analysis.keywords or []),
    )

    resume_input = ResumeMatchInput(
        skills=tuple(resume_analysis.skills or []),
        experience_summary=resume_analysis.experience_summary,
        education_summary=resume_analysis.education_summary,
        projects_summary=resume_analysis.projects_summary,
    )

    result = MatchingEngine().match(job_input, resume_input)

    repository = JobMatchRepository(session)

    match = await repository.create(
        job_id=job_id,
        resume_id=request.resume_id,
        score=result.score,
        required_skills_score=result.required_skills_score,
        preferred_skills_score=result.preferred_skills_score,
        experience_score=result.experience_score,
        education_score=result.education_score,
        keywords_score=result.keywords_score,
        matched_required_skills=list(result.matched_required_skills),
        missing_required_skills=list(result.missing_required_skills),
        matched_preferred_skills=list(result.matched_preferred_skills),
        missing_preferred_skills=list(result.missing_preferred_skills),
        explanations=list(result.explanations),
    )

    await session.commit()
    await session.refresh(match)

    return JobMatchResponse.model_validate(match, from_attributes=True)


@router.get(
    "/{job_id}/matches/latest",
    response_model=JobMatchResponse,
    summary="Get the latest job match",
    description=(
        "Return the latest persisted match between a job and a resume."
    ),
)
async def get_latest_job_match(
    job_id: UUID,
    resume_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUserResponse = Depends(get_current_user),
) -> JobMatchResponse:
    job = await session.get(Job, job_id)

    if job is None or job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    resume = await session.get(Resume, resume_id)

    if resume is None or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    repository = JobMatchRepository(session)

    match = await repository.get_latest(
        job_id=job_id,
        resume_id=resume_id,
    )

    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job match not found",
        )

    return JobMatchResponse.model_validate(match, from_attributes=True)


@router.get(
    "/{job_id}/matches/history",
    response_model=JobMatchHistoryResponse,
    summary="Get job match history",
    description=(
        "Return all persisted matches between a job and a resume, "
        "ordered from newest to oldest."
    ),
)
async def get_job_match_history(
    job_id: UUID,
    resume_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUserResponse = Depends(get_current_user),
) -> JobMatchHistoryResponse:
    job = await session.get(Job, job_id)

    if job is None or job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    resume = await session.get(Resume, resume_id)

    if resume is None or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    repository = JobMatchRepository(session)

    matches = await repository.list_history(
        job_id=job_id,
        resume_id=resume_id,
    )

    return JobMatchHistoryResponse(
        matches=[
            JobMatchResponse.model_validate(
                match,
                from_attributes=True,
            )
            for match in matches
        ]
    )