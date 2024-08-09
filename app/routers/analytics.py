from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.models import User
from app.repository.analytics import analytics_service
from app.repository.questions import question_repository
from app.schemas.analytics import (
    MemberQuizCompletion,
    QuizAverageScore,
    QuizCompletion,
    UserAverageScore,
    UserQuizWeeklyScores,
    WeeklyScores,
)
from app.services.auth import auth_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/user/average-score", response_model=UserAverageScore)
async def get_user_average_score(
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    average_score = await analytics_service.get_user_average_score(db, current_user.id)
    return UserAverageScore(average_score=average_score)


@router.get("/user/quiz-scores", response_model=List[QuizAverageScore])
async def get_user_quiz_scores(
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    quiz_scores = await analytics_service.get_user_quiz_scores(db, current_user.id)
    return quiz_scores


@router.get("/user/quiz-completions", response_model=List[QuizCompletion])
async def get_user_quiz_completions(
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    quiz_completions = await analytics_service.get_user_quiz_completions(db, current_user.id)
    return quiz_completions


@router.get("/company/{company_id}/weekly-average-scores", response_model=List[WeeklyScores])
async def get_company_weekly_average_scores(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await question_repository.check_if_admin(db, current_user.id, company_id)
    weekly_scores = await analytics_service.get_company_weekly_average_scores(db, company_id)
    return weekly_scores


@router.get(
    "/company/{company_id}/user/{user_id}/quiz-scores-over-time",
    response_model=List[UserQuizWeeklyScores],
)
async def get_user_quiz_scores_over_time(
    company_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await question_repository.check_if_admin(db, current_user.id, company_id)

    await analytics_service.is_user_member_of_company(db, user_id, company_id)

    weekly_scores = await analytics_service.get_user_quiz_scores_over_time(db, user_id, company_id)
    return weekly_scores


@router.get("/company/{company_id}/quiz-completions", response_model=List[MemberQuizCompletion])
async def get_company_quiz_completions(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await question_repository.check_if_admin(db, current_user.id, company_id)

    quiz_completions = await analytics_service.get_company_quiz_completions(db, company_id)
    return quiz_completions
