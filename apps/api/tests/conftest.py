import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.auth import get_current_user
from app.db.session import get_db_session
from app.main import app
from app.schemas.user import CurrentUserResponse

from contextlib import asynccontextmanager

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    pool_pre_ping=True,
)

TestingSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

TEST_USER = CurrentUserResponse(
    id="test-user-id",
    email="test@example.com",
    name="Test User",
)


TEST_USER_2 = CurrentUserResponse(
    id="test-user-id-2",
    email="test2@example.com",
    name="Test User 2",
)

async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


async def override_get_current_user() -> CurrentUserResponse:
    return TEST_USER


app.dependency_overrides[get_db_session] = override_get_db_session
app.dependency_overrides[get_current_user] = override_get_current_user



    
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client

@pytest_asyncio.fixture
async def as_second_user():
    @asynccontextmanager
    async def switch_user():
        async def override_second_user() -> CurrentUserResponse:
            return TEST_USER_2

        original_override = app.dependency_overrides[get_current_user]

        app.dependency_overrides[get_current_user] = override_second_user

        try:
            yield
        finally:
            app.dependency_overrides[get_current_user] = original_override

    return switch_user


@pytest_asyncio.fixture(autouse=True)
async def setup_test_user() -> AsyncGenerator[None, None]:
    async with TestingSessionLocal() as session:
        for user in (TEST_USER, TEST_USER_2):
            await session.execute(
                text(
                    """
                    INSERT INTO "user" (id, name, email, "emailVerified", "createdAt", "updatedAt")
                    VALUES (
                        :id,
                        :name,
                        :email,
                        true,
                        NOW(),
                        NOW()
                    )
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                },
            )

        await session.commit()

    yield