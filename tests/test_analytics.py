from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Member, QuizResult
from app.repository.analytics import AnalyticsService
from app.schemas.analytics import (
    MemberQuizCompletion,
    QuizAverageScore,
    QuizCompletion,
    QuizWeeklyScore,
    UserWeeklyScore,
)


@pytest.fixture
def mock_db_session():
    return AsyncMock(AsyncSession)


@pytest.fixture
def mock_quiz_result_data():
    return QuizResult(
        user_id=1,
        company_id=1,
        quiz_id=1,
        correct_answers=5,
        total_questions=10,
        score=50.0,
        completed_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_get_user_average_score(mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar.return_value = 75.0

    with patch.object(mock_db_session, "execute", return_value=mock_result):
        analytics_service = AnalyticsService()
        average_score = await analytics_service.get_user_average_score(db=mock_db_session, user_id=1)

        assert average_score == 75.0


@pytest.mark.asyncio
async def test_get_user_quiz_scores(mock_db_session, mock_quiz_result_data):
    mock_result = MagicMock()
    mock_result.all.return_value = [
        (1, 75.0, datetime(2023, 1, 1), datetime(2023, 1, 10)),
    ]

    with patch.object(mock_db_session, "execute", return_value=mock_result):
        analytics_service = AnalyticsService()
        scores = await analytics_service.get_user_quiz_scores(
            db=mock_db_session,
            user_id=1,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 10),
        )

        assert len(scores) == 1
        assert scores[0] == QuizAverageScore(
            quiz_id=1,
            average_score=75.0,
            first_completed=datetime(2023, 1, 1),
            last_completed=datetime(2023, 1, 10),
        )


@pytest.mark.asyncio
async def test_get_user_quiz_completions(mock_db_session):
    mock_result = MagicMock()
    mock_result.all.return_value = [
        (1, datetime(2023, 1, 10)),
    ]

    with patch.object(mock_db_session, "execute", return_value=mock_result):
        analytics_service = AnalyticsService()
        completions = await analytics_service.get_user_quiz_completions(db=mock_db_session, user_id=1)

        assert len(completions) == 1
        assert completions[0] == QuizCompletion(
            quiz_id=1,
            last_completed=datetime(2023, 1, 10),
        )


@pytest.mark.asyncio
async def test_get_company_quiz_results(mock_db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        (1, datetime(2023, 1, 10), 75.0),
    ]

    with patch.object(mock_db_session, "execute", return_value=mock_result):
        analytics_service = AnalyticsService()
        results = await analytics_service.get_company_quiz_results(db=mock_db_session, company_id=1)

        assert len(results) == 1
        assert results[0] == (1, datetime(2023, 1, 10), 75.0)


@pytest.mark.asyncio
async def test_get_company_weekly_average_scores(mock_db_session):
    with patch.object(
        AnalyticsService,
        "get_company_quiz_results",
        return_value=[
            (1, datetime(2023, 1, 3), 75.0),
            (1, datetime(2023, 1, 10), 85.0),
        ],
    ):
        analytics_service = AnalyticsService()
        weekly_scores = await analytics_service.get_company_weekly_average_scores(db=mock_db_session, company_id=1)

        assert len(weekly_scores) == 2
        assert weekly_scores[0].week_start == datetime(2023, 1, 2)
        assert weekly_scores[0].week_end == datetime(2023, 1, 8)
        assert weekly_scores[0].user_scores[0] == UserWeeklyScore(user_id=1, average_score=75.0)
        assert weekly_scores[1].week_start == datetime(2023, 1, 9)
        assert weekly_scores[1].week_end == datetime(2023, 1, 15)
        assert weekly_scores[1].user_scores[0] == UserWeeklyScore(user_id=1, average_score=85.0)


@pytest.mark.asyncio
async def test_is_user_member_of_company(mock_db_session):
    mock_member = Member(user_id=1, company_id=1)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_member

    with patch.object(mock_db_session, "execute", return_value=mock_result):
        analytics_service = AnalyticsService()
        is_member = await analytics_service.is_user_member_of_company(db=mock_db_session, user_id=1, company_id=1)

        assert is_member is True


@pytest.mark.asyncio
async def test_get_user_quiz_scores_over_time(mock_db_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        (1, datetime(2023, 1, 3), 75.0),
        (1, datetime(2023, 1, 10), 85.0),
    ]

    with patch.object(mock_db_session, "execute", return_value=mock_result):
        analytics_service = AnalyticsService()
        weekly_scores = await analytics_service.get_user_quiz_scores_over_time(
            db=mock_db_session, user_id=1, company_id=1
        )

        assert len(weekly_scores) == 2
        assert weekly_scores[0].week_start == datetime(2023, 1, 2).date()
        assert weekly_scores[0].week_end == datetime(2023, 1, 8).date()
        assert weekly_scores[0].quiz_scores[0] == QuizWeeklyScore(quiz_id=1, average_score=75.0)
        assert weekly_scores[1].week_start == datetime(2023, 1, 9).date()
        assert weekly_scores[1].week_end == datetime(2023, 1, 15).date()
        assert weekly_scores[1].quiz_scores[0] == QuizWeeklyScore(quiz_id=1, average_score=85.0)


@pytest.mark.asyncio
async def test_get_company_quiz_completions(mock_db_session):
    mock_result = MagicMock()
    mock_result.all.return_value = [
        (1, datetime(2023, 1, 10)),
    ]

    with patch.object(mock_db_session, "execute", return_value=mock_result):
        analytics_service = AnalyticsService()
        completions = await analytics_service.get_company_quiz_completions(db=mock_db_session, company_id=1)

        assert len(completions) == 1
        assert completions[0] == MemberQuizCompletion(
            user_id=1,
            last_completed=datetime(2023, 1, 10),
        )
