from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

from typing import Any

class JobInsight(Base):
    __tablename__ = "job_insight"

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

    match_score: Mapped[int] = mapped_column(
        nullable=False,
    )

    matching_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    missing_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    strengths: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    weaknesses: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    recommendations: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    overall_assessment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    raw_insight: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
