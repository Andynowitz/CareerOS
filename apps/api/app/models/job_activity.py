from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JobActivityType(str, enum.Enum):
    CREATED = "created"
    STATUS_CHANGED = "status_changed"
    NOTE = "note"
    EMAIL = "email"
    PHONE_CALL = "phone_call"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTION = "rejection"
    OTHER = "other"


class JobActivity(Base):
    __tablename__ = "job_activity"

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

    user_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type: Mapped[JobActivityType] = mapped_column(
        SAEnum(
            JobActivityType,
            name="job_activity_type",
            native_enum=True,
            values_callable=lambda enum_type: [
                item.value for item in enum_type
            ],
        ),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    old_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    new_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )