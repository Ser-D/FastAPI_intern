from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.models.users import User
from app.repository.quizzes import quiz_repository
from app.schemas.quizzes import QuestionBase, Quiz, QuizCreate, QuizRunResponse, QuizWithQuestions
from app.services.auth import auth_service

router = APIRouter(prefix="/quizzes/{company_id}/quizzes", tags=["quizzes"])


@router.post("/", response_model=Quiz)
async def create_quiz_endpoint(
    company_id: int,
    quiz: QuizCreate,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await quiz_repository.check_if_admin(db, user_id=current_user.id, company_id=company_id)

    created_quiz = await quiz_repository.create_quiz(db=db, quiz=quiz, company_id=company_id, user_id=current_user.id)
    return created_quiz


@router.get("/", response_model=List[Quiz])
async def get_quizzes_endpoint(
    company_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await quiz_repository.check_if_admin(db, user_id=current_user.id, company_id=company_id)

    quizzes = await quiz_repository.get_quizzes(
        db=db, company_id=company_id, user_id=current_user.id, skip=skip, limit=limit
    )
    return quizzes


@router.get("/{quiz_id}", response_model=QuizWithQuestions)
async def get_quiz_with_questions(
    company_id: int,
    quiz_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await quiz_repository.check_if_admin(db, user_id=current_user.id, company_id=company_id)

    quiz, questions = await quiz_repository.get_quiz_with_questions(db, quiz_id)
    quiz_with_questions = QuizWithQuestions(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        questions=[
            QuestionBase(
                id=q.id,
                text=q.text,
                answer_options=q.answer_options,
                correct_answers=q.correct_answers,
            )
            for q in questions
        ],
    )
    return quiz_with_questions


@router.delete("/{quiz_id}", response_model=None)
async def delete_quiz_endpoint(
    company_id: int,
    quiz_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await quiz_repository.check_if_admin(db, user_id=current_user.id, company_id=company_id)

    await quiz_repository.delete_quiz(db=db, quiz_id=quiz_id, company_id=company_id, user_id=current_user.id)
    return None


@router.post("/quizzes/{quiz_id}/run")
async def run_quiz_endpoint(
    quiz_id: int,
    responses: List[QuizRunResponse],
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    company_id = await quiz_repository.check_if_member(db, user_id=current_user.id, quiz_id=quiz_id)

    result = await quiz_repository.run_quiz(
        db=db,
        quiz_id=quiz_id,
        responses=responses,
        user_id=current_user.id,
        company_id=company_id,
    )
    return result
