from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.ai.analyzers.job_analyzer import JobAnalysisResult
from app.ai.analyzers.resume_analyzer import ResumeAnalysisResult
from app.models.job_analysis import JobAnalysis
from app.models.resume_analysis import ResumeAnalysis
from app.services.job_analysis import JobAnalysisService
from app.services.resume_analysis import ResumeAnalysisService


@pytest.mark.asyncio
async def test_job_analysis_service_persists_analysis():
    job_id = uuid4()

    analyzer = AsyncMock()
    repository = AsyncMock()

    analyzer.analyze.return_value = JobAnalysisResult(
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker"],
        responsibilities=["Develop backend services"],
        experience_requirements="2+ years",
        education_requirements="Bachelor's degree",
        keywords=["Python", "FastAPI"],
        salary_information={"min": 3000, "max": 4500},
    )

    expected_analysis = JobAnalysis(
        job_id=job_id,
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker"],
        responsibilities=["Develop backend services"],
        experience_requirements="2+ years",
        education_requirements="Bachelor's degree",
        keywords=["Python", "FastAPI"],
        salary_information={"min": 3000, "max": 4500},
        raw_analysis={
            "required_skills": ["Python", "FastAPI"],
            "preferred_skills": ["Docker"],
            "responsibilities": ["Develop backend services"],
            "experience_requirements": "2+ years",
            "education_requirements": "Bachelor's degree",
            "keywords": ["Python", "FastAPI"],
            "salary_information": {"min": 3000, "max": 4500},
        },
    )

    repository.create.return_value = expected_analysis

    service = JobAnalysisService(
        analyzer=analyzer,
        repository=repository,
    )

    result = await service.analyze_job(
        job_id=job_id,
        job_description="Python developer with FastAPI experience.",
    )

    assert result == expected_analysis

    analyzer.analyze.assert_awaited_once_with(
        "Python developer with FastAPI experience."
    )
    repository.create.assert_awaited_once()

    created_analysis = repository.create.call_args.args[0]

    assert created_analysis.job_id == job_id
    assert created_analysis.required_skills == ["Python", "FastAPI"]
    assert created_analysis.preferred_skills == ["Docker"]
    assert created_analysis.keywords == ["Python", "FastAPI"]


@pytest.mark.asyncio
async def test_resume_analysis_service_persists_analysis():
    resume_id = uuid4()

    analyzer = AsyncMock()
    repository = AsyncMock()

    analyzer.analyze.return_value = ResumeAnalysisResult(
        skills=["Java", "C#", "SQL"],
        experience_summary="Software development experience.",
        education_summary="Bachelor's degree in Software Engineering.",
        projects_summary="Developed several software projects.",
    )

    expected_analysis = ResumeAnalysis(
        resume_id=resume_id,
        skills=["Java", "C#", "SQL"],
        experience_summary="Software development experience.",
        education_summary="Bachelor's degree in Software Engineering.",
        projects_summary="Developed several software projects.",
        raw_analysis={
            "skills": ["Java", "C#", "SQL"],
            "experience_summary": "Software development experience.",
            "education_summary": "Bachelor's degree in Software Engineering.",
            "projects_summary": "Developed several software projects.",
        },
    )

    repository.create.return_value = expected_analysis

    service = ResumeAnalysisService(
        analyzer=analyzer,
        repository=repository,
    )

    result = await service.analyze_resume(
        resume_id=resume_id,
        resume_text="Java, C#, SQL. Bachelor of Software Engineering.",
    )

    assert result == expected_analysis

    analyzer.analyze.assert_awaited_once_with(
        "Java, C#, SQL. Bachelor of Software Engineering."
    )
    repository.create.assert_awaited_once()

    created_analysis = repository.create.call_args.args[0]

    assert created_analysis.resume_id == resume_id
    assert created_analysis.skills == ["Java", "C#", "SQL"]
    assert created_analysis.experience_summary == "Software development experience."
    assert created_analysis.education_summary == "Bachelor's degree in Software Engineering."
    