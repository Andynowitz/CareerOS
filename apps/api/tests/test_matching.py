from app.matching.matcher import MatchingEngine
from app.matching.models import JobMatchInput, ResumeMatchInput


def test_matching_all_skills_returns_perfect_score() -> None:
    job = JobMatchInput(
        required_skills=("C#", ".NET", "SQL"),
        preferred_skills=("Git",),
        experience_requirements="software development",
        education_requirements="computer science",
        keywords=("backend",),
    )

    resume = ResumeMatchInput(
        skills=("C Sharp", ".NET", "SQL", "Git"),
        experience_summary="Software development experience",
        education_summary="Computer Science degree",
        projects_summary="Backend project",
    )

    result = MatchingEngine().match(job, resume)

    assert result.score == 100
    assert result.required_skills_score == 1.0
    assert result.preferred_skills_score == 1.0
    assert result.missing_required_skills == ()
    assert result.missing_preferred_skills == ()


def test_matching_missing_required_skill_reduces_score() -> None:
    job = JobMatchInput(
        required_skills=("C#", ".NET", "SQL", "Docker"),
        preferred_skills=(),
        experience_requirements=None,
        education_requirements=None,
        keywords=(),
    )

    resume = ResumeMatchInput(
        skills=("C Sharp", ".NET", "SQL"),
        experience_summary=None,
        education_summary=None,
        projects_summary=None,
    )

    result = MatchingEngine().match(job, resume)

    assert result.required_skills_score == 0.75
    assert result.missing_required_skills == ("docker",)
    assert result.score == 88


def test_matching_empty_requirements_are_neutral() -> None:
    job = JobMatchInput(
        required_skills=(),
        preferred_skills=(),
        experience_requirements=None,
        education_requirements=None,
        keywords=(),
    )

    resume = ResumeMatchInput(
        skills=(),
        experience_summary=None,
        education_summary=None,
        projects_summary=None,
    )

    result = MatchingEngine().match(job, resume)

    assert result.score == 100
    assert result.explanations


def test_matching_is_deterministic() -> None:
    job = JobMatchInput(
        required_skills=("C#", ".NET", "SQL"),
        preferred_skills=("Git", "Docker"),
        experience_requirements="software development",
        education_requirements="computer science",
        keywords=("backend", "api"),
    )

    resume = ResumeMatchInput(
        skills=("C Sharp", ".NET", "Git"),
        experience_summary="Software development",
        education_summary="Computer Science",
        projects_summary="Backend API",
    )

    engine = MatchingEngine()

    first = engine.match(job, resume)
    second = engine.match(job, resume)

    assert first == second