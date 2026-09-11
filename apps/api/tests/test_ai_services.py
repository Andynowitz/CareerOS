from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.ai.analyzers.job_analyzer import JobAnalysisResult
from app.ai.analyzers.resume_analyzer import ResumeAnalysisResult
from app.models.job_analysis import JobAnalysis
from app.models.resume_analysis import ResumeAnalysis
from app.services.job_analysis import JobAnalysisService
from app.services.resume_analysis import ResumeAnalysisService
from app.ai.analyzers.job_insight_analyzer import JobInsightResult
from app.services.job_insight import JobInsightService


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


@pytest.mark.asyncio
async def test_job_insight_service():
    job_id = uuid4()
    resume_id = uuid4()

    class MockAnalyzer:
        async def analyze(self, job_analysis, resume_analysis):
            return JobInsightResult(
                match_score=82,
                matching_skills=["Python", "SQL"],
                missing_skills=["Kubernetes"],
                strengths=["Strong backend experience"],
                weaknesses=["Limited cloud experience"],
                recommendations=["Highlight backend projects"],
                overall_assessment="Strong match",
            )

    class MockRepository:
        async def create(self, insight):
            return insight

    service = JobInsightService(
        analyzer=MockAnalyzer(),
        repository=MockRepository(),
    )

    result = await service.analyze_job(
        job_id=job_id,
        resume_id=resume_id,
        job_analysis={
            "required_skills": ["Python", "SQL"],
        },
        resume_analysis={
            "skills": ["Python", "SQL"],
        },
    )

    assert result.job_id == job_id
    assert result.resume_id == resume_id
    assert result.match_score == 82
    assert result.matching_skills == ["Python", "SQL"]
    assert result.missing_skills == ["Kubernetes"]
    assert result.overall_assessment == "Strong match"


@pytest.mark.asyncio
async def test_job_analysis_service_persists_result():
    analyzer = AsyncMock()
    repository = AsyncMock()

    analyzer.analyze.return_value = JobAnalysisResult(
        required_skills=["Python"],
        preferred_skills=["Docker"],
        responsibilities=["Develop APIs"],
        experience_requirements="2 years",
        education_requirements="Bachelor's degree",
        keywords=["Python", "API"],
        salary_information={"currency": "EUR"},
    )

    saved_analysis = MagicMock()
    repository.create.return_value = saved_analysis

    service = JobAnalysisService(
        analyzer=analyzer,
        repository=repository,
    )

    result = await service.analyze_job(
        job_id=MagicMock(),
        job_description="Python backend developer.",
    )

    analyzer.analyze.assert_awaited_once_with(
        "Python backend developer."
    )
    repository.create.assert_awaited_once()

    analysis = repository.create.await_args.args[0]

    assert analysis.required_skills == ["Python"]
    assert analysis.preferred_skills == ["Docker"]
    assert analysis.responsibilities == ["Develop APIs"]
    assert analysis.experience_requirements == "2 years"
    assert analysis.education_requirements == "Bachelor's degree"
    assert analysis.keywords == ["Python", "API"]
    assert analysis.salary_information == {"currency": "EUR"}
    assert analysis.raw_analysis == analyzer.analyze.return_value.model_dump()

    assert result is saved_analysis


@pytest.mark.asyncio
async def test_resume_analysis_service_persists_result():
    analyzer = AsyncMock()
    repository = AsyncMock()

    analyzer.analyze.return_value = ResumeAnalysisResult(
        skills=["Python", "C#"],
        experience_summary="Backend development.",
        education_summary="Bachelor's degree.",
        projects_summary="Several software projects.",
    )

    saved_analysis = MagicMock()
    repository.create.return_value = saved_analysis

    service = ResumeAnalysisService(
        analyzer=analyzer,
        repository=repository,
    )

    resume_id = MagicMock()

    result = await service.analyze_resume(
        resume_id=resume_id,
        resume_text="Software engineer with Python experience.",
    )

    analyzer.analyze.assert_awaited_once_with(
        "Software engineer with Python experience."
    )
    repository.create.assert_awaited_once()

    analysis = repository.create.await_args.args[0]

    assert analysis.resume_id == resume_id
    assert analysis.skills == ["Python", "C#"]
    assert analysis.experience_summary == "Backend development."
    assert analysis.education_summary == "Bachelor's degree."
    assert analysis.projects_summary == "Several software projects."
    assert analysis.raw_analysis == analyzer.analyze.return_value.model_dump()

    assert result is saved_analysis


@pytest.mark.asyncio
async def test_job_insight_service_persists_result():
    analyzer = AsyncMock()
    repository = AsyncMock()

    analyzer.analyze.return_value = JobInsightResult(
        match_score=85,
        matching_skills=["Python", "FastAPI"],
        missing_skills=["Kubernetes"],
        strengths=["Strong backend experience"],
        weaknesses=["Limited Kubernetes"],
        recommendations=["Learn Kubernetes"],
        overall_assessment="Strong candidate.",
    )

    saved_insight = MagicMock()
    repository.create.return_value = saved_insight

    service = JobInsightService(
        analyzer=analyzer,
        repository=repository,
    )

    job_id = MagicMock()
    resume_id = MagicMock()

    result = await service.analyze_job(
        job_id=job_id,
        resume_id=resume_id,
        job_analysis={"required_skills": ["Python", "FastAPI"]},
        resume_analysis={"skills": ["Python", "FastAPI"]},
    )

    analyzer.analyze.assert_awaited_once_with(
        job_analysis={"required_skills": ["Python", "FastAPI"]},
        resume_analysis={"skills": ["Python", "FastAPI"]},
    )

    repository.create.assert_awaited_once()

    insight = repository.create.await_args.args[0]

    assert insight.job_id == job_id
    assert insight.resume_id == resume_id
    assert insight.match_score == 85
    assert insight.matching_skills == ["Python", "FastAPI"]
    assert insight.missing_skills == ["Kubernetes"]
    assert insight.strengths == ["Strong backend experience"]
    assert insight.weaknesses == ["Limited Kubernetes"]
    assert insight.recommendations == ["Learn Kubernetes"]
    assert insight.overall_assessment == "Strong candidate."
    assert insight.raw_insight == analyzer.analyze.return_value.model_dump()

    assert result is saved_insight