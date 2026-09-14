from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JobMatch(Base):
    __tablename__ = "job_matches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    required_skills_score: Mapped[float] = mapped_column(
        nullable=False,
    )

    preferred_skills_score: Mapped[float] = mapped_column(
        nullable=False,
    )

    experience_score: Mapped[float] = mapped_column(
        nullable=False,
    )

    education_score: Mapped[float] = mapped_column(
        nullable=False,
    )

    keywords_score: Mapped[float] = mapped_column(
        nullable=False,
    )

    matched_required_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    missing_required_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    matched_preferred_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    missing_preferred_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    explanations: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )