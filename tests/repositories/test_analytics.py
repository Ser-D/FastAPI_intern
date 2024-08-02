import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.analytics import AnalyticsService
from app.models import QuizResult


@pytest.mark.asyncio
async def test_get_user_average_score(db_session: AsyncSession):
    analytics_service = AnalyticsService()

    # Попередні дані для тесту
    user_id = 1
    company_id = 1
    quiz_id = 1
    await db_session.execute(QuizResult.__table__.insert().values(
        user_id=user_id,
        company_id=company_id,
        quiz_id=quiz_id,
        correct_answers=5,
        total_questions=10,
        score=85,
        completed_at=datetime.now()
    ))
    await db_session.commit()

    average_score = await analytics_service.get_user_average_score(db_session, user_id)
    assert average_score == 85.0
