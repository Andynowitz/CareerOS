from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    experience_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    education_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    projects_summary: Mapped[str | None] = mapped_column(
        Text,
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