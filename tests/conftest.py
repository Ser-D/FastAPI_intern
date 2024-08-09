from unittest.mock import AsyncMock, patch

import pytest
from faker import Faker

from app.schemas.members import MemberCreate
from app.schemas.quizzes import QuizCreate, QuizRunResponse, QuizUpdate


@pytest.fixture(scope="session")
def faker():
    return Faker()


@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock()
    return mock_session


@pytest.fixture
def mock_user_model():
    user = AsyncMock()
    user.create = AsyncMock()
    user.get_user_by_email = AsyncMock()
    user.update = AsyncMock()
    user.delete = AsyncMock()
    return user


@pytest.fixture
def user_data(faker):
    return {
        "firstname": faker.first_name(),
        "lastname": faker.last_name(),
        "email": faker.email(),
        "hashed_password": faker.password(),
        "city": faker.city(),
        "phone": faker.phone_number(),
        "avatar": faker.image_url(),
    }


@pytest.fixture
def company_data(faker):
    return {
        "name": faker.company(),
        "description": faker.catch_phrase(),
        "owner_id": 1,
        "is_visible": True,
    }


@pytest.fixture
def member_data(faker):
    return MemberCreate(user_id=1, company_id=1, type="invite", status="pending")


@pytest.fixture
def quiz_create_data(faker):
    return QuizCreate(
        title=faker.sentence(),
        description=faker.text(),
        question_ids=[1, 2, 3],
        usage_count=0,
    )


@pytest.fixture
def quiz_update_data(faker):
    return QuizUpdate(
        title=faker.sentence(),
        description=faker.text(),
        question_ids=[1, 2, 3],
        usage_count=1,
    )


@pytest.fixture
def quiz_run_responses(faker):
    return [
        QuizRunResponse(selected_answers=[faker.random_int(min=1, max=10)])
        for _ in range(3)
    ]


@pytest.fixture
def mock_redis_client():
    with patch("app.db.redis.redis_client", new_callable=AsyncMock) as mock:
        yield mock
