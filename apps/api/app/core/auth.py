from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.user import CurrentUserResponse


async def get_current_user(
    session_token: str | None = Cookie(default=None, alias="better-auth.session_token"),
    db: AsyncSession = Depends(get_db_session),
) -> CurrentUserResponse:
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    session_token = session_token.split(".", 1)[0]

    result = await db.execute(
        text(
            """
            SELECT
                u.id,
                u.email,
                u.name,
                s."expiresAt"
            FROM "session" AS s
            INNER JOIN "user" AS u
                ON u.id = s."userId"
            WHERE s.token = :token
            LIMIT 1
            """
        ),
        {"token": session_token},
    )

    row = result.mappings().first()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )

    expires_at = row["expiresAt"]

    if expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )

    return CurrentUserResponse(
        id=row["id"],
        email=row["email"],
        name=row["name"],
    )