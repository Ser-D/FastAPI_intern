import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.db.redis import redis_client
from app.models.users import User
from app.repository.quizresult import QuizResultRepository
from app.repository.quizzes import quiz_repository
from app.schemas.quizresult import UserAverageScoreInCompany, UserAverageScoreSystemwide
from app.services.auth import auth_service
from app.services.redis import redis_service

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


# TODO: remove
@router.get("/quiz/responses/{user_id}/{quiz_id}")
async def get_quiz_responses(user_id: int, quiz_id: int):
    key = f"quiz_responses:{user_id}:{quiz_id}"

    redis_data = await redis_client.get(key)

    if redis_data is None:
        raise HTTPException(status_code=404, detail="Quiz responses not found")

    quiz_responses = json.loads(redis_data)

    return quiz_responses


@router.get("/quizzes/responses", response_model=list)
async def get_user_quiz_result(
    quiz_id: int = None, current_user: User = Depends(auth_service.get_current_user)
):
    return await redis_service.get_user_quiz_responses(quiz_id, current_user.id)


@router.get("/company/{company_id}/quiz_responses", response_model=list)
async def get_company_quiz_responses(
    company_id: int,
    quiz_id: int = None,
    user_id: int = None,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await quiz_repository.check_if_admin(db, current_user.id, company_id)

    return await redis_service.get_company_quiz_responses(quiz_id, company_id, user_id)


@router.get("/company/{company_id}/quiz/{quiz_id}/export")
async def export_quiz_results(
    company_id: int,
    quiz_id: int,
    format: str = Query("json", enum=["json", "csv"]),
    save_path: str = Query("/Users", description="Path to save the exported file"),
    user_id: int = None,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await quiz_repository.check_if_admin(db, current_user.id, company_id)

    results = await redis_service.get_company_quiz_responses(
        quiz_id, company_id, user_id
    )

    return redis_service.export_quiz_results(results, format, save_path)
