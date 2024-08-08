from unittest.mock import patch

import pytest
from fastapi import HTTPException
from jose import jwt

from app.core.config import settings
from app.models.users import User


@pytest.mark.asyncio
async def test_verify_password(auth):
    hashed_password = auth.get_password_hash("password")
    assert auth.verify_password("password", hashed_password)


@pytest.mark.asyncio
async def test_create_user(auth, mock_db, mock_user):
    mock_db.execute.return_value.scalars().scalar_one_or_none.return_value = None
    mock_db.add.return_value = None

    with patch.object(User, "create", return_value=mock_user):
        user = await auth.create_user(
            mock_db, email=mock_user.email, hashed_password=mock_user.hashed_password
        )
        assert user.email == mock_user.email


@pytest.mark.asyncio
async def test_authenticate_user(auth, mock_db, mock_user):
    with patch.object(User, "get_user_by_email", return_value=mock_user):
        user = await auth.authenticate_user(mock_db, mock_user.email, "password")
        assert user.email == mock_user.email


@pytest.mark.asyncio
async def test_authenticate_user_invalid(auth, mock_db):
    with patch.object(User, "get_user_by_email", return_value=None):
        with pytest.raises(HTTPException):
            await auth.authenticate_user(mock_db, "invalid@example.com", "password")


@pytest.mark.asyncio
async def test_create_access_token(auth, mock_user):
    token = await auth.create_access_token(data={"sub": mock_user.email})
    decoded = jwt.decode(
        token, settings.SECRET_KEY_JWT, algorithms=[settings.ALGORITHM]
    )
    assert decoded["sub"] == mock_user.email


@pytest.mark.asyncio
async def test_get_current_user(auth, mock_db, mock_user, valid_token):
    with patch.object(User, "get_user_by_email", return_value=mock_user):
        user = await auth.get_current_user(token=valid_token, db=mock_db)
        assert user.email == mock_user.email


@pytest.mark.asyncio
async def test_get_current_user_invalid(auth, mock_db, expired_token):
    with pytest.raises(HTTPException):
        await auth.get_current_user(token=expired_token, db=mock_db)
