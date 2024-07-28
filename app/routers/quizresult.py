from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.quizresult import QuizResultRepository
from app.models.users import User
from app.services.auth import auth_service
from app.db.postgres import get_database
from app.schemas.quizresult import UserAverageScoreInCompany, UserAverageScoreSystemwide

router = APIRouter(prefix="/quiz_results", tags=["quiz_results"])


@router.get("/user/{user_id}/company/{company_id}/average_score", response_model=UserAverageScoreInCompany)
async def get_user_average_score_in_company(
        user_id: int,
        company_id: int,
        db: AsyncSession = Depends(get_database),
        current_user: User = Depends(auth_service.get_current_user)
):
    repo = QuizResultRepository()
    average_score = await repo.calculate_user_average_score_in_company(db, user_id, company_id)

    if not average_score:
        raise HTTPException(status_code=404, detail="No quiz results found for the user in the specified company")

    return average_score


@router.get("/user/{user_id}/average_score", response_model=UserAverageScoreSystemwide)
async def get_user_average_score_systemwide(
        user_id: int,
        db: AsyncSession = Depends(get_database),
        current_user: User = Depends(auth_service.get_current_user)
):
    repo = QuizResultRepository()
    average_score = await repo.calculate_user_average_score_systemwide(db, user_id)

    if not average_score:
        raise HTTPException(status_code=404, detail="No quiz results found for the user")

    return average_score
