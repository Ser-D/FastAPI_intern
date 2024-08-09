from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import patch

import pytest

from app.models.members import Member
from app.models.quiz import Quiz
from app.models.users import User
from app.services.scheduler import check_quiz_completions


@pytest.mark.asyncio
@patch("app.services.scheduler.fetch_quizzes")
@patch("app.services.scheduler.fetch_members")
@patch("app.services.scheduler.fetch_user")
@patch(
    "app.repository.notifications.notification_repo.create_incomplete_quiz_notification"
)
@patch("app.repository.quizzes.quiz_repository.get_last_completion_time")
async def test_check_quiz_completions(
    mock_get_last_completion_time,
    mock_create_incomplete_quiz_notification,
    mock_fetch_user,
    mock_fetch_members,
    mock_fetch_quizzes,
):
    mock_quiz = Quiz(id=1, company_id=1)
    mock_member = Member(id=1, company_id=1, user_id=1)
    mock_user = User(id=1)

    mock_fetch_quizzes.return_value = [mock_quiz]
    mock_fetch_members.return_value = [mock_member]
    mock_fetch_user.return_value = mock_user

    mock_get_last_completion_time.return_value = None

    await check_quiz_completions()

    mock_create_incomplete_quiz_notification.assert_called_once_with(mock.ANY, 1, 1)

    mock_create_incomplete_quiz_notification.reset_mock()

    mock_get_last_completion_time.return_value = datetime.utcnow() - timedelta(hours=25)

    await check_quiz_completions()

    mock_create_incomplete_quiz_notification.assert_called_once_with(mock.ANY, 1, 1)

    mock_create_incomplete_quiz_notification.reset_mock()

    mock_get_last_completion_time.return_value = datetime.utcnow() - timedelta(hours=23)

    await check_quiz_completions()

    mock_create_incomplete_quiz_notification.assert_not_called()
