from unittest.mock import AsyncMock

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.models.users import User
from app.services.auth import Auth


@pytest_asyncio.fixture
async def async_session():
    # Setup: створюємо сесію бази даних
    async for session in get_database():
        yield session


@pytest_asyncio.fixture
async def mock_db():
    db = AsyncMock(AsyncSession)
    return db


@pytest_asyncio.fixture
async def auth():
    return Auth()


@pytest_asyncio.fixture
def mock_user():
    return User(
        id=1,
        email="test@example.com",
        hashed_password=Auth().get_password_hash("password"),
        is_active=True,
    )


@pytest_asyncio.fixture
async def valid_token(mock_user):
    data = {"sub": mock_user.email}
    return await Auth().create_access_token(data)


@pytest_asyncio.fixture
async def expired_token(mock_user):
    data = {"sub": mock_user.email, "exp": 0}
    return await Auth().create_access_token(data)
