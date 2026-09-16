from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchingWeights:
    required_skills: float = 0.50
    preferred_skills: float = 0.20
    experience: float = 0.15
    education: float = 0.10
    keywords: float = 0.05

    def __post_init__(self) -> None:
        total = (
            self.required_skills
            + self.preferred_skills
            + self.experience
            + self.education
            + self.keywords
        )

        if abs(total - 1.0) > 1e-9:
            raise ValueError("Matching weights must sum to 1.0")


DEFAULT_MATCHING_WEIGHTS = MatchingWeights()