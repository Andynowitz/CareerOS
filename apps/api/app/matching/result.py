from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchResult:
    score: int

    required_skills_score: float
    preferred_skills_score: float
    experience_score: float
    education_score: float
    keywords_score: float

    matched_required_skills: tuple[str, ...]
    missing_required_skills: tuple[str, ...]

    matched_preferred_skills: tuple[str, ...]
    missing_preferred_skills: tuple[str, ...]

    explanations: tuple[str, ...]