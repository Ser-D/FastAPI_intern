from unittest.mock import patch

import pytest

from app.models.users import User


@pytest.mark.asyncio
async def test_create_user(mock_db_session, user_data):
    with patch.object(User, "create", return_value=User(**user_data)) as mock_create:
        user = await User.create(db=mock_db_session, **user_data)

        assert user.email == user_data["email"]
        mock_create.assert_awaited_once_with(db=mock_db_session, **user_data)


@pytest.mark.asyncio
async def test_get_user_by_email(mock_db_session, user_data):
    email = user_data["email"]

    with patch.object(User, "get_user_by_email", return_value=User(**user_data)) as mock_get_user_by_email:
        user = await User.get_user_by_email(db=mock_db_session, email=email)

        assert user.email == email
        mock_get_user_by_email.assert_awaited_once_with(db=mock_db_session, email=email)


@pytest.mark.asyncio
async def test_update_user(mock_db_session, user_data):
    updated_firstname = user_data["firstname"]
    user = User(**user_data)
    user.firstname = updated_firstname

    with patch.object(User, "update", return_value=user) as mock_update:
        updated_user = await User.update(db=mock_db_session, user_id=1, firstname=updated_firstname)

        assert updated_user.firstname == updated_firstname
        mock_update.assert_awaited_once_with(db=mock_db_session, user_id=1, firstname=updated_firstname)


@pytest.mark.asyncio
async def test_delete_user(mock_db_session, user_data):
    with patch.object(User, "delete", return_value=None) as mock_delete:
        await User.delete(db=mock_db_session, user_id=1)

        mock_delete.assert_awaited_once_with(db=mock_db_session, user_id=1)
