import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.db.redis import redis_client
from app.models.users import User
from app.repository.quizresult import QuizResultRepository
from app.schemas.quizresult import UserAverageScoreInCompany, UserAverageScoreSystemwide
from app.services.auth import auth_service

router = APIRouter(prefix="/quiz_results", tags=["quiz_results"])


@router.get(
    "/user/{user_id}/company/{company_id}/average_score",
    response_model=UserAverageScoreInCompany,
)
async def get_user_average_score_in_company(
    user_id: int,
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    repo = QuizResultRepository()
    average_score = await repo.calculate_user_average_score_in_company(
        db, user_id, company_id
    )

    if not average_score:
        raise HTTPException(
            status_code=404,
            detail="No quiz results found for the user in the specified company",
        )

    return average_score


@router.get("/user/{user_id}/average_score", response_model=UserAverageScoreSystemwide)
async def get_user_average_score_systemwide(
    user_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    repo = QuizResultRepository()
    average_score = await repo.calculate_user_average_score_systemwide(db, user_id)

    if not average_score:
        raise HTTPException(
            status_code=404, detail="No quiz results found for the user"
        )

    return average_score


@router.get("/quiz/responses/{user_id}/{quiz_id}")
async def get_quiz_responses(user_id: int, quiz_id: int):
    key = f"quiz_responses:{user_id}:{quiz_id}"

    redis_data = await redis_client.get(key)

    if redis_data is None:
        raise HTTPException(status_code=404, detail="Quiz responses not found")

    quiz_responses = json.loads(redis_data)

    return quiz_responses
