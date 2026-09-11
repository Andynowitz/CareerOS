from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(Text, primary_key=True)

    name: Mapped[str] = mapped_column(Text, nullable=False)

    email: Mapped[str] = mapped_column(Text, nullable=False)

    email_verified: Mapped[bool] = mapped_column(
        "emailVerified",
        Boolean,
        nullable=False,
    )

    image: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )