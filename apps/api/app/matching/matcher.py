from __future__ import annotations

import re
from dataclasses import dataclass

from app.matching.config import (
    DEFAULT_MATCHING_WEIGHTS,
    MatchingWeights,
)
from app.matching.models import JobMatchInput, ResumeMatchInput
from app.matching.result import MatchResult
from app.matching.skill_matcher import SkillMatchResult, SkillMatcher


@dataclass(frozen=True)
class MatchingEngine:
    weights: MatchingWeights = DEFAULT_MATCHING_WEIGHTS

    def match(
        self,
        job: JobMatchInput,
        resume: ResumeMatchInput,
    ) -> MatchResult:
        resume_text = self._resume_text(resume)

        required = SkillMatcher.match(
            job.required_skills,
            resume.skills,
            resume_text,
        )

        preferred = SkillMatcher.match(
            job.preferred_skills,
            resume.skills,
            resume_text,
        )

        experience_score = self._experience_match(
            job.experience_requirements,
            resume,
        )

        education_score = self._education_match(
            job.education_requirements,
            resume.education_summary,
        )

        keywords_score = self._keyword_match(
            job.keywords,
            resume,
        )

        weighted_score = (
            required.score * self.weights.required_skills
            + preferred.score * self.weights.preferred_skills
            + experience_score * self.weights.experience
            + education_score * self.weights.education
            + keywords_score * self.weights.keywords
        )

        score = round(weighted_score * 100)

        explanations = self._build_explanations(
            required,
            preferred,
            experience_score,
            education_score,
            keywords_score,
        )

        return MatchResult(
            score=score,
            required_skills_score=required.score,
            preferred_skills_score=preferred.score,
            experience_score=experience_score,
            education_score=education_score,
            keywords_score=keywords_score,
            matched_required_skills=required.matched,
            missing_required_skills=required.missing,
            matched_preferred_skills=preferred.matched,
            missing_preferred_skills=preferred.missing,
            explanations=explanations,
        )

    @staticmethod
    def _resume_text(resume: ResumeMatchInput) -> str:
        return " ".join(
            part
            for part in (
                resume.experience_summary,
                resume.education_summary,
                resume.projects_summary,
            )
            if part
        )

    @staticmethod
    def _experience_match(
        requirement: str | None,
        resume: ResumeMatchInput,
    ) -> float:
        if not requirement:
            return 1.0

        if not resume.experience_summary:
            return 0.0

        requirement_lower = requirement.lower()
        experience_lower = resume.experience_summary.lower()

        scores: list[float] = []

        # Extract the required number of years from statements such as
        # "at least 2 years of professional experience".
        year_matches = re.findall(
            r"(?:at least\s+)?(\d+(?:\.\d+)?)\s+years?",
            requirement_lower,
        )

        required_years = [
            float(value)
            for value in year_matches
        ]

        # Estimate professional experience from explicit date ranges.
        date_ranges = re.findall(
            r"(\w+\s+\d{4})\s+to\s+(\w+\s+\d{4})",
            experience_lower,
        )

        experience_months = 0

        for start, end in date_ranges:
            start_match = re.search(r"(\w+)\s+(\d{4})", start)
            end_match = re.search(r"(\w+)\s+(\d{4})", end)

            if not start_match or not end_match:
                continue

            start_month = MatchingEngine._month_number(
                start_match.group(1)
            )
            start_year = int(start_match.group(2))

            end_month = MatchingEngine._month_number(
                end_match.group(1)
            )
            end_year = int(end_match.group(2))

            months = (
                (end_year - start_year) * 12
                + (end_month - start_month)
                + 1
            )

            if months > 0:
                experience_months += months

        if required_years and experience_months:
            actual_years = experience_months / 12

            required_average = sum(required_years) / len(
                required_years
            )

            scores.append(
                min(actual_years / required_average, 1.0)
            )

        # Check whether the candidate's experience is relevant to
        # the technologies mentioned in the requirement.
        relevant_terms = {
            term
            for term in (
                "java",
                "javascript",
                "typescript",
                "angular",
                "react",
                "node.js",
                "nodejs",
                "fullstack",
                "backend",
                "frontend",
                "software developer",
                "software engineer",
            )
            if term in requirement_lower
        }

        if relevant_terms:
            matched_terms = sum(
                1
                for term in relevant_terms
                if term in experience_lower
            )

            scores.append(
                matched_terms / len(relevant_terms)
            )

        if not scores:
            return MatchingEngine._text_match(
                requirement,
                resume.experience_summary,
            )

        return sum(scores) / len(scores)

    @staticmethod
    def _month_number(month: str) -> int:
        months = {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }

        return months.get(month.lower(), 1)

    @staticmethod
    def _education_match(
        requirement: str | None,
        candidate: str | None,
    ) -> float:
        if not requirement:
            return 1.0

        if not candidate:
            return 0.0

        requirement_lower = requirement.lower()
        candidate_lower = candidate.lower()

        score = 0.0

        # Degree level.
        if "bachelor" in requirement_lower:
            if "bachelor" in candidate_lower:
                score += 0.5

                # The job asks for a completed degree.
                if "completed" in requirement_lower:
                    if (
                        "present" in candidate_lower
                        or "current" in candidate_lower
                        or "ongoing" in candidate_lower
                    ):
                        score += 0.0
                    else:
                        score += 0.5
                else:
                    score += 0.5

        elif "master" in requirement_lower:
            if "master" in candidate_lower:
                score += 1.0

        # Field of study.
        if (
            "information technology" in requirement_lower
            or "similar field" in requirement_lower
        ):
            relevant_fields = (
                "information technology",
                "software engineering",
                "computer science",
                "informatics",
                "software engineering and management",
            )

            if any(
                field in candidate_lower
                for field in relevant_fields
            ):
                score = min(score + 0.0, 1.0)

                # If degree level was already satisfied, keep it.
                if "bachelor" in candidate_lower:
                    score = max(score, 0.75)

        if score > 0:
            return min(score, 1.0)

        return MatchingEngine._text_match(
            requirement,
            candidate,
        )

    @staticmethod
    def _text_match(
        requirement: str | None,
        candidate: str | None,
    ) -> float:
        if not requirement:
            return 1.0

        if not candidate:
            return 0.0

        requirement_words = set(
            re.findall(
                r"\b[a-z0-9+#.]+\b",
                requirement.lower(),
            )
        )

        candidate_words = set(
            re.findall(
                r"\b[a-z0-9+#.]+\b",
                candidate.lower(),
            )
        )

        stop_words = {
            "a",
            "an",
            "and",
            "or",
            "the",
            "with",
            "of",
            "for",
            "to",
            "in",
            "on",
            "as",
            "is",
            "are",
            "be",
            "years",
            "year",
            "experience",
            "strong",
            "good",
            "excellent",
            "fluent",
            "knowledge",
        }

        meaningful_words = {
            word
            for word in requirement_words
            if word not in stop_words
        }

        if not meaningful_words:
            return 1.0

        overlap = meaningful_words & candidate_words

        return len(overlap) / len(meaningful_words)

    @staticmethod
    def _keyword_match(
        keywords: tuple[str, ...],
        resume: ResumeMatchInput,
    ) -> float:
        if not keywords:
            return 1.0

        resume_text = MatchingEngine._resume_text(resume).lower()

        matched = sum(
            1
            for keyword in keywords
            if keyword.strip().lower() in resume_text
        )

        return matched / len(keywords)

    def _build_explanations(
        self,
        required: SkillMatchResult,
        preferred: SkillMatchResult,
        experience_score: float,
        education_score: float,
        keywords_score: float,
    ) -> tuple[str, ...]:       
        explanations: list[str] = []

        required_total = (
            len(required.matched) + len(required.missing)
        )

        if required_total:
            explanations.append(
                f"Matched {len(required.matched)} of "
                f"{required_total} required skills."
            )

        if required.missing:
            explanations.append(
                "Missing required skills: "
                + ", ".join(required.missing)
                + "."
            )

        preferred_total = (
            len(preferred.matched) + len(preferred.missing)
        )

        if preferred_total == 0:
            explanations.append(
                "No preferred skills specified for this job."
            )
        else:
            explanations.append(
                f"Matched {len(preferred.matched)} of "
                f"{preferred_total} preferred skills."
            )

            if preferred.matched:
                explanations.append(
                    "Matched preferred skills: "
                    + ", ".join(preferred.matched)
                    + "."
                )

            if preferred.missing:
                explanations.append(
                    "Missing preferred skills: "
                    + ", ".join(preferred.missing)
                    + "."
                )

        explanations.append(
            f"Experience match: {round(experience_score * 100)}%."
        )

        explanations.append(
            f"Education match: {round(education_score * 100)}%."
        )

        explanations.append(
            f"Keyword match: {round(keywords_score * 100)}%."
        )

        return tuple(explanations)