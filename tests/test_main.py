from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "detail": "ok", "result": "working"}


@patch("app.main.get_database", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_healthchecker(mock_get_database):
    mock_session = AsyncMock()
    mock_get_database.return_value = mock_session
    mock_session.execute.return_value.fetchone.return_value = [1]

    response = await client.get("/healthchecker")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI"}

    mock_session.execute.return_value.fetchone.return_value = None
    response = await client.get("/healthchecker")
    assert response.status_code == 500
    assert response.json() == {"detail": "Database is not configured correctly"}

    mock_session.execute.side_effect = Exception("Database error")
    response = await client.get("/healthchecker")
    assert response.status_code == 500
    assert response.json() == {"detail": "Error connecting to the database"}


@patch("app.main.redis_client", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_test_redis_connection(mock_redis_client):
    mock_redis_client.ping.return_value = True
    mock_redis_client.get.return_value = "test_value"

    response = await client.get("/test_redis")
    assert response.status_code == 200
    assert response.json() == "test_value"

    mock_redis_client.ping.side_effect = Exception("Redis error")
    response = await client.get("/test_redis")
    assert response.status_code == 500
    assert response.json() == {"detail": "Error during Redis test: Redis error"}
