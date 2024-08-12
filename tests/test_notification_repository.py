from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select

from app.models import User
from app.models.notifications import Notification
from app.repository.notifications import NotificationRepository


@pytest.fixture
def user_data(faker):
    return {
        "id": 1,
        "firstname": faker.first_name(),
        "lastname": faker.last_name(),
        "email": faker.email(),
        "hashed_password": faker.password(),
        "city": faker.city(),
        "phone": faker.phone_number(),
        "avatar": faker.image_url(),
    }


@pytest.fixture
def notification_data(faker, user_data):
    return {
        "user_id": user_data["id"],
        "message": faker.sentence(),
        "created_at": faker.date_time(),
        "is_read": False,
    }


@pytest.mark.asyncio
async def test_create_quiz_notification(mock_db_session):
    company_id = 1
    quiz_id = 1
    users = [
        User(id=1, email="user1@example.com"),
        User(id=2, email="user2@example.com"),
    ]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = users
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db_session.execute.return_value = mock_result

    notification_repo = NotificationRepository()

    with patch.object(mock_db_session, "commit", new_callable=AsyncMock) as mock_commit:
        with patch.object(mock_db_session, "add", new_callable=AsyncMock) as mock_add:
            await notification_repo.create_quiz_notification(db=mock_db_session, company_id=company_id, quiz_id=quiz_id)

            assert mock_add.call_count == len(users)
            for i, user in enumerate(users):
                args, _ = mock_add.call_args_list[i]
                notification = args[0]
                print(f"Testing user: {user.id}, notification.user_id: {notification.user_id}")  # Debug output
                assert notification.user_id == user.id


@pytest.mark.asyncio
async def test_get_user_notifications(mock_db_session):
    user_id = 1
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [Notification(user_id=user_id, message="Test Message")]

    mock_result.scalars.return_value = mock_scalars
    mock_db_session.execute.return_value = mock_result

    with patch.object(mock_db_session, "execute", return_value=mock_result) as mock_execute:
        notification_repo = NotificationRepository()
        notifications = await notification_repo.get_user_notifications(mock_db_session, user_id)

        assert len(notifications) == 1
        assert notifications[0].user_id == user_id
        assert notifications[0].message == "Test Message"
        mock_execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_incomplete_quiz_notification(mock_db_session, user_data, notification_data):
    with patch("app.core.config.logger.info") as mock_logger:
        notification_repo = NotificationRepository()
        await notification_repo.create_incomplete_quiz_notification(
            db=mock_db_session, user_id=user_data["id"], quiz_id=1
        )

        called_notification = mock_db_session.add.call_args[0][0]
        assert called_notification.user_id == user_data["id"]
        assert (
            called_notification.message
            == f"Please complete the quiz with ID 1. You have not completed it in the last 24 hours."
        )
        assert isinstance(called_notification.created_at, datetime)

        mock_db_session.commit.assert_awaited_once()
        mock_logger.assert_any_call(f"Creating notification for user {user_data['id']} and quiz 1")
        mock_logger.assert_any_call(f"Notification created for user {user_data['id']} for quiz 1")


@pytest.mark.asyncio
async def test_get_user_notifications(mock_db_session, notification_data):
    notifications = [Notification(**notification_data)]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = notifications

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    with patch.object(mock_db_session, "execute", return_value=mock_result) as mock_execute_call:
        notification_repo = NotificationRepository()
        fetched_notifications = await notification_repo.get_user_notifications(
            db=mock_db_session, user_id=notification_data["user_id"]
        )

        assert fetched_notifications == notifications

        mock_execute_call.assert_awaited_once()
        args, kwargs = mock_execute_call.await_args
        assert str(args[0]) == str(select(Notification).filter(Notification.user_id == notification_data["user_id"]))


@pytest.mark.asyncio
async def test_mark_notification_as_read(mock_db_session, notification_data):
    notification = Notification(**notification_data)
    notification_id = notification_data["user_id"]

    with patch.object(mock_db_session, "get", return_value=notification) as mock_get:
        notification_repo = NotificationRepository()
        updated_notification = await notification_repo.mark_notification_as_read(
            db=mock_db_session,
            notification_id=notification_id,
            user_id=notification_data["user_id"],
        )

        assert updated_notification.is_read is True
        mock_get.assert_awaited_once_with(Notification, notification_id)
        mock_db_session.commit.assert_awaited_once()
        mock_db_session.refresh.assert_awaited_once_with(notification)
