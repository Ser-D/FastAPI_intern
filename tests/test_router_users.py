from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.users import User

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_users():
    users = [
        User(id=1, email="user1@example.com"),
        User(id=2, email="user2@example.com"),
    ]

    with patch("app.models.users.User.get_all", new_callable=AsyncMock, return_value=users):
        response = client.get("/users/users")
        assert response.status_code == 200
        assert len(response.json()["items"]) == 2
