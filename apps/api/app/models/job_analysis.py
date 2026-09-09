from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JobAnalysis(Base):
    __tablename__ = "job_analysis"

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

    required_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    preferred_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    responsibilities: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    experience_requirements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    education_requirements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    keywords: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    salary_information: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    raw_analysis: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )