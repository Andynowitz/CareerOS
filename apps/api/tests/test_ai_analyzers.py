from unittest.mock import AsyncMock

import pytest

from app.ai.analyzers.job_analyzer import JobAnalysisResult, JobAnalyzer
from app.ai.analyzers.resume_analyzer import ResumeAnalysisResult, ResumeAnalyzer


@pytest.mark.asyncio
async def test_job_analyzer_returns_structured_result():
    mock_client = AsyncMock()

    mock_client.analyze.return_value = JobAnalysisResult(
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker"],
        responsibilities=["Develop backend services"],
        experience_requirements="2+ years of experience",
        education_requirements="Bachelor's degree in Computer Science",
        keywords=["Python", "FastAPI", "Docker"],
        salary_information={"min": 3000, "max": 4500},
    )

    analyzer = JobAnalyzer(mock_client)

    result = await analyzer.analyze(
        """
        We are looking for a Python developer.

        Requirements:
        - Python
        - FastAPI
        - 2+ years of experience

        Docker experience is preferred.
        """
    )

    assert result.required_skills == ["Python", "FastAPI"]
    assert result.preferred_skills == ["Docker"]
    assert result.responsibilities == ["Develop backend services"]
    assert result.experience_requirements == "2+ years of experience"
    assert result.education_requirements == "Bachelor's degree in Computer Science"
    assert result.keywords == ["Python", "FastAPI", "Docker"]
    assert result.salary_information == {"min": 3000, "max": 4500}

    mock_client.analyze.assert_awaited_once()


@pytest.mark.asyncio
async def test_resume_analyzer_returns_structured_result():
    mock_client = AsyncMock()

    mock_client.analyze.return_value = ResumeAnalysisResult(
        skills=["Java", "C#", "SQL"],
        experience_summary="Software development experience.",
        education_summary="Bachelor's degree in Software Engineering.",
        projects_summary="Developed several software projects.",
    )

    analyzer = ResumeAnalyzer(mock_client)

    result = await analyzer.analyze(
        """
        Andreas Alexandru

        Skills:
        Java, C#, SQL

        Education:
        Bachelor of Software Engineering

        Projects:
        Several software development projects
        """
    )

    assert result.skills == ["Java", "C#", "SQL"]
    assert result.experience_summary == "Software development experience."
    assert result.education_summary == "Bachelor's degree in Software Engineering."
    assert result.projects_summary == "Developed several software projects."

    mock_client.analyze.assert_awaited_once()