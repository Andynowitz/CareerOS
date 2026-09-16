from __future__ import annotations

import re


class SkillNormalizer:
    """Normalizes skill names for deterministic matching."""

    _ALIASES: dict[str, str] = {
        "c sharp": "c#",
        "csharp": "c#",
        "dotnet": ".net",
        "dot net": ".net",
        "asp net": "asp.net",
        "aspnet": "asp.net",
        "javascript": "javascript",
        "js": "javascript",
        "typescript": "typescript",
        "ts": "typescript",
        "postgres": "postgresql",
        "postgresql": "postgresql",
        "mssql": "sql server",
        "ms sql": "sql server",
        "microsoft sql server": "sql server",
        "sql server": "sql server",
        "reactjs": "react",
        "react.js": "react",
        "nodejs": "node.js",
        "node": "node.js",
    }

    @classmethod
    def normalize(cls, skill: str) -> str:
        """Return a canonical representation of a skill."""
        normalized = skill.strip().lower()
        normalized = re.sub(r"\s+", " ", normalized)

        return cls._ALIASES.get(normalized, normalized)

    @classmethod
    def normalize_many(cls, skills: tuple[str, ...]) -> tuple[str, ...]:
        """Normalize multiple skills and remove duplicates."""
        normalized = {cls.normalize(skill) for skill in skills if skill.strip()}
        return tuple(sorted(normalized))
