# tests/services/test_auth.py

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from app.services.auth import auth_service

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    user_data = {
        "firstname": "Test",
        "lastname": "User",
        "email": "test@example.com",
        "password": "testpassword"
    }
    new_user = await auth_service.create_user(db_session, **user_data)
    assert new_user.email == user_data["email"]

@pytest.mark.asyncio
async def test_authenticate_user(db_session: AsyncSession):
    user_data = {
        "firstname": "Test",
        "lastname": "User",
        "email": "test@example.com",
        "password": "testpassword"
    }
    new_user = await auth_service.create_user(db_session, **user_data)
    authenticated_user = await auth_service.authenticate_user(db_session, user_data["email"], user_data["password"])
    assert authenticated_user.email == user_data["email"]

@pytest.mark.asyncio
async def test_create_access_token():
    data = {"sub": "test@example.com"}
    access_token = await auth_service.create_access_token(data)
    assert access_token is not None

@pytest.mark.asyncio
async def test_get_current_user(async_client: AsyncClient, db_session: AsyncSession, get_token: str):
    token = await auth_service.create_access_token({"sub": "test@example.com"})
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/some_protected_route", headers=headers)
    assert response.status_code == 200
    current_user = await auth_service.get_current_user(token, db_session)
    assert current_user.email == "test@example.com"
