from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.repository.quizresult import QuizResultRepository


@pytest.mark.asyncio
async def test_create_quiz_result(mock_db_session):
    quiz_result_data = {
        "user_id": 1,
        "company_id": 1,
        "quiz_id": 1,
        "correct_answers": 5,
        "total_questions": 10,
        "score": 50.0,
    }

    with patch.object(mock_db_session, "add", new_callable=AsyncMock) as mock_add:
        with patch.object(
            mock_db_session, "commit", new_callable=AsyncMock
        ) as mock_commit:
            with patch.object(
                mock_db_session, "refresh", new_callable=AsyncMock
            ) as mock_refresh:
                quiz_result_repo = QuizResultRepository()
                created_quiz_result = await quiz_result_repo.create_quiz_result(
                    db=mock_db_session, **quiz_result_data
                )

                created_quiz_result.completed_at = datetime.utcnow()

                assert created_quiz_result.user_id == quiz_result_data["user_id"]
                assert created_quiz_result.company_id == quiz_result_data["company_id"]
                assert created_quiz_result.quiz_id == quiz_result_data["quiz_id"]
                assert (
                    created_quiz_result.correct_answers
                    == quiz_result_data["correct_answers"]
                )
                assert (
                    created_quiz_result.total_questions
                    == quiz_result_data["total_questions"]
                )
                assert created_quiz_result.score == quiz_result_data["score"]
                assert created_quiz_result.completed_at is not None
                mock_add.assert_called_once()
                mock_commit.assert_awaited_once()
                mock_refresh.assert_awaited_once_with(created_quiz_result)


@pytest.mark.asyncio
async def test_calculate_user_average_score_in_company(mock_db_session):
    result_data = {"total_questions": 50, "total_correct_answers": 40}
    mock_result = MagicMock()
    mock_result.fetchone.return_value = MagicMock(**result_data)

    with patch.object(
        mock_db_session, "execute", new_callable=AsyncMock, return_value=mock_result
    ):
        quiz_result_repo = QuizResultRepository()
        average_score = await quiz_result_repo.calculate_user_average_score_in_company(
            db=mock_db_session, user_id=1, company_id=1
        )

        assert average_score["user_id"] == 1
        assert average_score["company_id"] == 1
        assert average_score["total_questions"] == result_data["total_questions"]
        assert (
            average_score["total_correct_answers"]
            == result_data["total_correct_answers"]
        )
        assert average_score["percentage"] == (
            result_data["total_correct_answers"] / result_data["total_questions"] * 100
        )


@pytest.mark.asyncio
async def test_calculate_user_average_score_systemwide(mock_db_session):
    result_data = {"total_questions": 100, "total_correct_answers": 80}
    mock_result = MagicMock()
    mock_result.fetchone.return_value = MagicMock(**result_data)

    with patch.object(
        mock_db_session, "execute", new_callable=AsyncMock, return_value=mock_result
    ):
        quiz_result_repo = QuizResultRepository()
        average_score = await quiz_result_repo.calculate_user_average_score_systemwide(
            db=mock_db_session, user_id=1
        )

        assert average_score["user_id"] == 1
        assert average_score["total_questions"] == result_data["total_questions"]
        assert (
            average_score["total_correct_answers"]
            == result_data["total_correct_answers"]
        )
        assert average_score["percentage"] == (
            result_data["total_correct_answers"] / result_data["total_questions"] * 100
        )
