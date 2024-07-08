from unittest.mock import AsyncMock, patch

import pytest

from app.models.users import User
from app.repository.users import (
    create_user,
    delete_user,
    get_user_by_email,
    get_user_by_id,
    get_users,
    update_user,
)
from app.schemas.users import SignUpRequest, UserUpdateRequest


@pytest.fixture
def user_data():
    return {
        "email": "john.doe@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "city": "New York",
        "phone": "1234567890",
        "avatar": "http://example.com/avatar.png",
        "hashed_password": "hashedpassword",
    }


@pytest.fixture
def new_user(user_data):
    return User(**user_data)


@patch("app.repository.users.select")
@patch("app.repository.users.AsyncSession")
@pytest.mark.asyncio
async def test_get_user_by_email(mock_async_session, mock_select, user_data):
    db = mock_async_session.return_value
    db.execute.return_value.scalar_one_or_none.return_value = User(**user_data)
    result = await get_user_by_email("john.doe@example.com", db)
    assert result.email == user_data["email"]

    # Test case when user is not found
    db.execute.return_value.scalar_one_or_none.return_value = None
    result = await get_user_by_email("nonexistent@example.com", db)
    assert result is None


@patch("app.repository.users.AsyncSession")
@pytest.mark.asyncio
async def test_create_user(mock_async_session, user_data):
    db = mock_async_session.return_value
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    sign_up_request = SignUpRequest(
        **user_data, password1="password", password2="password"
    )
    result = await create_user(sign_up_request, db)
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result.email == user_data["email"]


@patch("app.repository.users.select")
@patch("app.repository.users.AsyncSession")
@pytest.mark.asyncio
async def test_get_user_by_id(mock_async_session, mock_select, user_data):
    db = mock_async_session.return_value
    db.execute.return_value.scalar_one_or_none.return_value = User(**user_data)
    result = await get_user_by_id(1, db)
    assert result.email == user_data["email"]

    # Test case when user is not found
    db.execute.return_value.scalar_one_or_none.return_value = None
    result = await get_user_by_id(999, db)
    assert result is None


@patch("app.repository.users.select")
@patch("app.repository.users.AsyncSession")
@pytest.mark.asyncio
async def test_get_users(mock_async_session, mock_select, user_data):
    db = mock_async_session.return_value
    db.execute.return_value.scalars.return_value.all.return_value = [User(**user_data)]
    result = await get_users(0, 10, db)
    assert len(result) == 1
    assert result[0].email == user_data["email"]

    # Test case when no users are found
    db.execute.return_value.scalars.return_value.all.return_value = []
    result = await get_users(0, 10, db)
    assert result == []


@patch("app.repository.users.AsyncSession")
@pytest.mark.asyncio
async def test_update_user(mock_async_session, user_data):
    db = mock_async_session.return_value
    db.execute.return_value.scalar_one_or_none.return_value = User(**user_data)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    update_request = UserUpdateRequest(firstname="Jane", lastname="Doe")
    result = await update_user(1, update_request, db)
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result.firstname == "Jane"
    assert result.lastname == "Doe"

    # Test case when user is not found
    db.execute.return_value.scalar_one_or_none.return_value = None
    result = await update_user(999, update_request, db)
    assert result is None


@patch("app.repository.users.AsyncSession")
@pytest.mark.asyncio
async def test_delete_user(mock_async_session, user_data):
    db = mock_async_session.return_value
    db.execute.return_value.scalar_one_or_none.return_value = User(**user_data)
    db.delete = AsyncMock()
    db.commit = AsyncMock()

    result = await delete_user(1, db)
    db.delete.assert_called_once()
    db.commit.assert_called_once()
    assert result.email == user_data["email"]

    # Test case when user is not found
    db.execute.return_value.scalar_one_or_none.return_value = None
    result = await delete_user(999, db)
    assert result is None
