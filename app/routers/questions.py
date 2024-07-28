from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.models.users import User
from app.repository.questions import question_repository
from app.schemas.questions import Question, QuestionCreate, QuestionUpdate
from app.services.auth import auth_service

router = APIRouter(prefix="/question/{company_id}/questions", tags=["questions"])


@router.post("/", response_model=Question)
async def create_question_endpoint(
    company_id: int,
    question: QuestionCreate,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    created_question = await question_repository.create_question(
        db=db, question=question, company_id=company_id, user_id=current_user.id
    )
    return created_question


@router.get("/", response_model=List[Question])
async def get_questions_endpoint(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    questions = await question_repository.get_questions(
        db=db, company_id=company_id, user_id=current_user.id
    )
    return questions


@router.put("/{question_id}", response_model=Question)
async def update_question_endpoint(
    company_id: int,
    question_id: int,
    question: QuestionUpdate,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    updated_question = await question_repository.update_question(
        db=db,
        question_id=question_id,
        question=question,
        company_id=company_id,
        user_id=current_user.id,
    )
    return updated_question
