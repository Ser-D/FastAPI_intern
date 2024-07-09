import unittest
from unittest.mock import AsyncMock, patch

from fastapi import BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.routers import users as users_router
from app.schemas.users import SignUpRequest, UserUpdateRequest


class TestAsyncUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.user = User(
            id=1,
            email="testuser@example.com",
            firstname="Test",
            lastname="User",
            city="Test City",
            phone="1234567890",
            avatar="http://example.com/avatar.png",
            hashed_password="hashedpassword",
        )
        self.session = AsyncMock(spec=AsyncSession)

    @patch("app.repository.users.get_user_by_email", new_callable=AsyncMock)
    async def test_signup(self, mock_get_user_by_email):
        mock_get_user_by_email.return_value = (
            None  # Імітуємо відсутність користувача з таким email
        )

        body = SignUpRequest(
            firstname="John",
            lastname="Doe",
            email="john.doe@example.com",
            password1="password",
            password2="password",
            city="New York",
            phone="1234567890",
            avatar="http://example.com/avatar.png",
        )
        self.session.add = AsyncMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        response = await users_router.signup(
            body, BackgroundTasks(), Request(scope={"type": "http"}), self.session
        )
        self.assertEqual(response.email, body.email)

    @patch("app.repository.users.get_users", new_callable=AsyncMock)
    async def test_get_users(self, mock_get_users):
        skip = 0
        limit = 10
        users = [
            self.user,
            User(
                id=2,
                email="testuser2@example.com",
                firstname="Test2",
                lastname="User2",
                city="Test City",
                phone="1234567890",
                avatar="http://example.com/avatar.png",
                hashed_password="hashedpassword",
            ),
        ]
        mock_get_users.return_value = users

        response = await users_router.get_users(skip=skip, limit=limit, db=self.session)
        self.assertEqual(len(response), 2)
        self.assertEqual(response[0].email, self.user.email)
        self.assertEqual(response[1].email, "testuser2@example.com")

    @patch("app.repository.users.get_user_by_id", new_callable=AsyncMock)
    async def test_get_user(self, mock_get_user_by_id):
        mock_get_user_by_id.return_value = self.user

        response = await users_router.get_user(user_id=1, db=self.session)
        self.assertEqual(response.email, self.user.email)

    @patch("app.repository.users.update_user", new_callable=AsyncMock)
    async def test_update_user(self, mock_update_user):
        body = UserUpdateRequest(
            firstname="Updated",
            lastname="User",
            email="updated@example.com",
            city="Updated City",
            phone="0987654321",
            avatar="http://example.com/updatedavatar.png",
        )
        updated_user = self.user
        updated_user.firstname = "Updated"
        updated_user.lastname = "User"
        updated_user.email = "updated@example.com"
        updated_user.city = "Updated City"
        updated_user.phone = "0987654321"
        updated_user.avatar = "http://example.com/updatedavatar.png"
        mock_update_user.return_value = updated_user

        response = await users_router.update_user(user_id=1, body=body, db=self.session)
        self.assertEqual(response.firstname, body.firstname)
        self.assertEqual(response.lastname, body.lastname)
        self.assertEqual(response.email, body.email)
        self.assertEqual(response.city, body.city)
        self.assertEqual(response.phone, body.phone)
        self.assertEqual(response.avatar, body.avatar)

    @patch("app.repository.users.delete_user", new_callable=AsyncMock)
    async def test_delete_user(self, mock_delete_user):
        mock_delete_user.return_value = (
            self.user
        )  # Імітуємо успішне видалення користувача

        response = await users_router.delete_user(user_id=1, db=self.session)
        self.assertIsNone(response)
        mock_delete_user.assert_awaited_once_with(1, self.session)


if __name__ == "__main__":
    unittest.main()
