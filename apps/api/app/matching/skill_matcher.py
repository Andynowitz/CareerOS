from __future__ import annotations

import re
from dataclasses import dataclass

from app.matching.skill_normalizer import SkillNormalizer


@dataclass(frozen=True)
class SkillMatchResult:
    score: float
    matched: tuple[str, ...]
    missing: tuple[str, ...]


class SkillMatcher:
    _STOP_WORDS = {
        "a",
        "an",
        "and",
        "at",
        "c1",
        "c2",
        "english",
        "excellent",
        "experience",
        "experienced",
        "fluent",
        "for",
        "good",
        "german",
        "knowledge",
        "level",
        "methods",
        "new",
        "of",
        "or",
        "supporting",
        "technologies",
        "the",
        "tools",
        "with",
    }

    @staticmethod
    def match(
        required_skills: tuple[str, ...],
        candidate_skills: tuple[str, ...],
        candidate_text: str | None = None,
    ) -> SkillMatchResult:
        required = set(
            SkillNormalizer.normalize_many(required_skills)
        )
        candidate = set(
            SkillNormalizer.normalize_many(candidate_skills)
        )

        if not required:
            return SkillMatchResult(
                score=1.0,
                matched=(),
                missing=(),
            )

        normalized_text = SkillMatcher._normalize_text(
            candidate_text or ""
        )

        matched: set[str] = set()

        for skill in required:
            if skill in candidate:
                matched.add(skill)
                continue

            if SkillMatcher._matches_text(
                skill,
                normalized_text,
            ):
                matched.add(skill)

        missing = required - matched
        score = len(matched) / len(required)

        return SkillMatchResult(
            score=score,
            matched=tuple(sorted(matched)),
            missing=tuple(sorted(missing)),
        )

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    @classmethod
    def _matches_text(
        cls,
        skill: str,
        text: str,
    ) -> bool:
        if not text:
            return False

        skill = cls._normalize_text(skill)

        # Exact phrase match.
        if skill in text:
            return True

        words = [
            word
            for word in re.findall(
                r"\b[a-z0-9+#.]+\b",
                skill,
            )
            if word not in cls._STOP_WORDS
        ]

        if not words:
            return False

        # A technical skill such as Java, React, C#, etc.
        # should require the actual skill token.
        if len(words) == 1:
            return bool(
                re.search(
                    rf"(?<![a-z0-9+#.])"
                    rf"{re.escape(words[0])}"
                    rf"(?![a-z0-9+#.])",
                    text,
                )
            )

        # For multi-word concepts, require at least half
        # of the meaningful words to occur in the resume.
        matched_words = sum(
            1
            for word in words
            if re.search(
                rf"(?<![a-z0-9+#.])"
                rf"{re.escape(word)}"
                rf"(?![a-z0-9+#.])",
                text,
            )
        )

        return matched_words / len(words) >= 0.5