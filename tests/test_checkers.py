from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "detail": "ok", "result": "working"}


@pytest.mark.asyncio
async def test_healthchecker():
    with patch("app.routers.checkers.get_database", new_callable=AsyncMock) as mock_get_database:
        mock_session = AsyncMock()
        mock_session.execute.return_value.fetchone.return_value = (1,)
        mock_get_database.return_value = mock_session

        response = client.get("/healthchecker")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to FastAPI"}

        mock_session.execute.side_effect = Exception("Test error")
        response = client.get("/healthchecker")
        assert response.status_code == 500
        assert response.json() == {"detail": "Error connecting to the database"}


@pytest.mark.asyncio
async def test_test_redis_connection():
    response = client.get("/test_redis")
    assert response.status_code == 200
    assert response.json() == "test_value"
