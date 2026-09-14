from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchingRules:
    required_skill_weight: float = 0.50
    preferred_skill_weight: float = 0.20
    experience_weight: float = 0.15
    education_weight: float = 0.10
    keyword_weight: float = 0.05

    required_skill_threshold: float = 0.70
    preferred_skill_threshold: float = 0.50

    def validate(self) -> None:
        weights = (
            self.required_skill_weight,
            self.preferred_skill_weight,
            self.experience_weight,
            self.education_weight,
            self.keyword_weight,
        )

        if any(weight < 0 for weight in weights):
            raise ValueError("Matching weights cannot be negative")

        if abs(sum(weights) - 1.0) > 1e-9:
            raise ValueError("Matching weights must sum to 1.0")

        if not 0 <= self.required_skill_threshold <= 1:
            raise ValueError("Required skill threshold must be between 0 and 1")

        if not 0 <= self.preferred_skill_threshold <= 1:
            raise ValueError("Preferred skill threshold must be between 0 and 1")


DEFAULT_MATCHING_RULES = MatchingRules()
DEFAULT_MATCHING_RULES.validate()