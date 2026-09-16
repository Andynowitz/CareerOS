from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class JobMatchInput:
    required_skills: tuple[str, ...]
    preferred_skills: tuple[str, ...]
    experience_requirements: str | None
    education_requirements: str | None
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class ResumeMatchInput:
    skills: tuple[str, ...]
    experience_summary: str | None
    education_summary: str | None
    projects_summary: str | None
