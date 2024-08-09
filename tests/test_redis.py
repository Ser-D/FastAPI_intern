import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.services.redis import RedisService, redis_service


@pytest.mark.asyncio
async def test_get_user_quiz_responses_found():
    quiz_id = 1
    user_id = 1
    key = f"quiz_responses:{user_id}:{quiz_id}"
    data = [{"response": "test"}]

    with patch(
        "app.db.redis.redis_client.get",
        new_callable=AsyncMock,
        return_value=json.dumps(data),
    ) as mock_get:
        result = await redis_service.get_user_quiz_responses(quiz_id, user_id)
        assert result == data
        mock_get.assert_awaited_once_with(key)


@pytest.mark.asyncio
async def test_get_user_quiz_responses_not_found():
    quiz_id = 1
    user_id = 1
    key = f"quiz_responses:{user_id}:{quiz_id}"

    with patch("app.db.redis.redis_client.get", new_callable=AsyncMock, return_value=None) as mock_get:
        with pytest.raises(HTTPException) as excinfo:
            await redis_service.get_user_quiz_responses(quiz_id, user_id)
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "No quiz responses found for this user and quiz."
        mock_get.assert_awaited_once_with(key)


@pytest.mark.asyncio
async def test_get_company_quiz_responses_found():
    quiz_id = 1
    company_id = 1
    user_id = 1
    data = [{}, {}, {}, {"quiz_data": {"company_id": company_id, "user_id": user_id}}]

    with patch("app.db.redis.redis_client.keys", new_callable=AsyncMock, return_value=["key1"]) as mock_keys:
        with patch(
            "app.db.redis.redis_client.get",
            new_callable=AsyncMock,
            return_value=json.dumps(data),
        ) as mock_get:
            result = await redis_service.get_company_quiz_responses(quiz_id, company_id, user_id)
            assert result == data
            mock_keys.assert_awaited_once_with(f"quiz_responses:*:{quiz_id}")
            mock_get.assert_awaited_once_with("key1")


@pytest.mark.asyncio
async def test_get_company_quiz_responses_not_found():
    quiz_id = 1
    company_id = 1
    user_id = 1
    data = [
        {},
        {},
        {},
        {"quiz_data": {"company_id": company_id + 1, "user_id": user_id + 1}},
    ]

    with patch("app.db.redis.redis_client.keys", new_callable=AsyncMock, return_value=["key1"]) as mock_keys:
        with patch(
            "app.db.redis.redis_client.get",
            new_callable=AsyncMock,
            return_value=json.dumps(data),
        ) as mock_get:
            with pytest.raises(HTTPException) as excinfo:
                await redis_service.get_company_quiz_responses(quiz_id, company_id, user_id)
            assert excinfo.value.status_code == 404
            assert excinfo.value.detail == "No quiz responses found for this user and quiz."
            mock_keys.assert_awaited_once_with(f"quiz_responses:*:{quiz_id}")
            mock_get.assert_awaited_once_with("key1")


def test_export_quiz_results_csv():
    results = [{"quiz_data": {"field1": "value1", "field2": "value2"}}]
    save_path = "tests/output"

    response = RedisService.export_quiz_results(results, "csv", save_path)

    assert isinstance(response, StreamingResponse)
    assert response.media_type == "text/csv"
    assert response.headers["Content-Disposition"] == "attachment; filename=quiz_results.csv"


def test_export_quiz_results_json():
    results = [{"quiz_data": {"field1": "value1", "field2": "value2"}}]
    save_path = "tests/output"

    response = RedisService.export_quiz_results(results, "json", save_path)

    assert isinstance(response, StreamingResponse)
    assert response.media_type == "application/json"
    assert response.headers["Content-Disposition"] == "attachment; filename=quiz_results.json"
