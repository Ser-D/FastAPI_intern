from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.members import Member
from app.models.question import Question as QuestionModel
from app.schemas.questions import QuestionCreate, QuestionUpdate


class QuestionRepository:
    async def check_if_admin(self, db: AsyncSession, user_id: int, company_id: int) -> None:
        admin_check = await db.execute(
            select(Member).where(
                Member.company_id == company_id,
                Member.user_id == user_id,
                Member.is_admin,
            )
        )
        admin = admin_check.scalar_one_or_none()
        if not admin:
            raise HTTPException(status_code=403, detail="Not authorized to perform this action")

    async def create_question(
        self, db: AsyncSession, question: QuestionCreate, company_id: int, user_id: int
    ) -> QuestionModel:
        await self.check_if_admin(db, user_id=user_id, company_id=company_id)

        if len(question.answer_options) < 2 or len(question.answer_options) > 4:
            raise HTTPException(
                status_code=400,
                detail="Number of answer options must be between 2 and 4.",
            )
        if any(int(correct_answer) > len(question.answer_options) for correct_answer in question.correct_answers):
            raise HTTPException(
                status_code=400,
                detail="Correct answers must be valid indices of answer options.",
            )

        db_question = QuestionModel(
            text=question.text,
            answer_options=question.answer_options,
            correct_answers=question.correct_answers,
            company_id=company_id,
        )
        db.add(db_question)
        await db.commit()
        await db.refresh(db_question)
        return db_question

    async def get_questions(self, db: AsyncSession, company_id: int, user_id: int) -> List[QuestionModel]:
        await self.check_if_admin(db, user_id=user_id, company_id=company_id)
        result = await db.execute(select(QuestionModel).where(QuestionModel.company_id == company_id))
        return result.scalars().all()

    async def update_question(
        self,
        db: AsyncSession,
        question_id: int,
        question: QuestionUpdate,
        company_id: int,
        user_id: int,
    ) -> QuestionModel:
        await self.check_if_admin(db, user_id=user_id, company_id=company_id)

        db_question = await db.get(QuestionModel, question_id)
        if not db_question or db_question.company_id != company_id:
            raise HTTPException(status_code=404, detail="Question not found")

        if len(question.answer_options) < 2 or len(question.answer_options) > 4:
            raise HTTPException(
                status_code=400,
                detail="Number of answer options must be between 2 and 4.",
            )
        if any(int(correct_answer) > len(question.answer_options) for correct_answer in question.correct_answers):
            raise HTTPException(
                status_code=400,
                detail="Correct answers must be valid indices of answer options.",
            )

        db_question.text = question.text
        db_question.answer_options = question.answer_options
        db_question.correct_answers = [str(answer) for answer in question.correct_answers]
        await db.commit()
        await db.refresh(db_question)
        return db_question


question_repository = QuestionRepository()
