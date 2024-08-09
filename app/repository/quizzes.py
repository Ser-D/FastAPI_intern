import json
from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import logger
from app.db.redis import redis_client
from app.models.members import Member
from app.models.question import Question as QuestionModel
from app.models.quiz import Quiz as QuizModel
from app.models.quizresult import QuizResult as QuizResultModel
from app.repository.notifications import notification_repo
from app.repository.quizresult import repo_quizresult
from app.schemas.quizzes import QuizCreate, QuizResponseRedis, QuizResult, QuizRunResponse, QuizUpdate


class QuizRepository:
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

    async def check_if_member(self, db: AsyncSession, user_id: int, quiz_id: int) -> int:
        quiz_result = await db.execute(select(QuizModel).filter_by(id=quiz_id))
        quiz = quiz_result.scalars().first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        member_check = await db.execute(
            select(Member).where(Member.company_id == quiz.company_id, Member.user_id == user_id)
        )
        member = member_check.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=403,
                detail="Not authorized - User is not a member of the company",
            )

        return quiz.company_id

    async def create_quiz(self, db: AsyncSession, quiz: QuizCreate, company_id: int, user_id: int) -> QuizModel:
        await self.check_if_admin(db, user_id=user_id, company_id=company_id)

        if len(quiz.question_ids) < 2:
            raise HTTPException(status_code=400, detail="A quiz must have at least two questions.")

        questions = await db.execute(select(QuestionModel).filter(QuestionModel.id.in_(quiz.question_ids)))
        questions = questions.scalars().all()

        if not all(q.company_id == company_id for q in questions):
            raise HTTPException(
                status_code=400,
                detail="All questions must belong to the same company as the quiz.",
            )

        db_quiz = QuizModel(
            title=quiz.title,
            description=quiz.description,
            question_ids=quiz.question_ids,
            usage_count=quiz.usage_count,
            company_id=company_id,
        )
        db.add(db_quiz)
        await db.commit()
        await db.refresh(db_quiz)

        await notification_repo.create_quiz_notification(db=db, company_id=company_id, quiz_id=db_quiz.id)

        return db_quiz

    async def get_quizzes(
        self,
        db: AsyncSession,
        company_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[QuizModel]:
        await self.check_if_admin(db, user_id=user_id, company_id=company_id)
        result = await db.execute(select(QuizModel).where(QuizModel.company_id == company_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def update_quiz(
        self,
        db: AsyncSession,
        quiz_id: int,
        quiz: QuizUpdate,
        company_id: int,
        user_id: int,
    ) -> QuizModel:
        await self.check_if_admin(db, user_id=user_id, company_id=company_id)

        db_quiz = await db.get(QuizModel, quiz_id)
        if not db_quiz or db_quiz.company_id != company_id:
            raise HTTPException(status_code=404, detail="Quiz not found")

        if len(quiz.question_ids) < 2:
            raise HTTPException(status_code=400, detail="A quiz must have at least two questions.")

        db_quiz.title = quiz.title
        db_quiz.description = quiz.description
        db_quiz.question_ids = quiz.question_ids
        db_quiz.usage_count = quiz.usage_count
        await db.commit()
        await db.refresh(db_quiz)
        return db_quiz

    async def delete_quiz(self, db: AsyncSession, quiz_id: int, company_id: int, user_id: int) -> None:
        await self.check_if_admin(db, user_id=user_id, company_id=company_id)

        db_quiz = await db.get(QuizModel, quiz_id)
        if not db_quiz or db_quiz.company_id != company_id:
            raise HTTPException(status_code=404, detail="Quiz not found")

        await db.delete(db_quiz)
        await db.commit()

    async def run_quiz(
        self,
        db: AsyncSession,
        quiz_id: int,
        responses: List[QuizRunResponse],
        user_id: int,
        company_id: int,
    ) -> QuizResult:
        db_quiz = await db.get(QuizModel, quiz_id)
        if not db_quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        db_questions = await db.execute(select(QuestionModel).filter(QuestionModel.id.in_(db_quiz.question_ids)))
        db_questions = db_questions.scalars().all()

        correct_answers_list = [
            sorted([str(answer) for answer in question.correct_answers]) for question in db_questions
        ]
        user_answers_list = [sorted([str(answer) for answer in response.selected_answers]) for response in responses]

        correct_answers_count = 0
        for correct_answers, user_answers in zip(correct_answers_list, user_answers_list):
            if correct_answers == user_answers:
                correct_answers_count += 1

        score = (correct_answers_count / len(correct_answers_list)) * 100

        await self.store_quiz_responses(
            db=db,
            user_id=user_id,
            quiz_id=quiz_id,
            responses=responses,
            correct_answers=correct_answers_count,
            total_questions=len(correct_answers_list),
        )

        quiz_result = await repo_quizresult.create_quiz_result(
            db=db,
            user_id=user_id,
            company_id=company_id,
            quiz_id=quiz_id,
            correct_answers=correct_answers_count,
            total_questions=len(correct_answers_list),
            score=score,
        )

        return quiz_result

    async def get_quiz_with_questions(self, db: AsyncSession, quiz_id: int) -> QuizModel:
        result = await db.execute(select(QuizModel).where(QuizModel.id == quiz_id))
        quiz = result.scalars().first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        questions_result = await db.execute(select(QuestionModel).where(QuestionModel.id.in_(quiz.question_ids)))
        questions = questions_result.scalars().all()

        return quiz, questions

    async def get_quiz_from_db(self, db: AsyncSession, quiz_id: int):
        result = await db.execute(select(QuizModel).filter_by(id=quiz_id))
        quiz = result.scalars().first()

        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        return quiz

    async def store_quiz_responses(
        self,
        db: AsyncSession,
        user_id: int,
        quiz_id: int,
        responses: List[QuizRunResponse],
        correct_answers=int,
        total_questions=int,
    ):
        key = f"quiz_responses:{user_id}:{quiz_id}"

        quiz, db_questions = await self.get_quiz_with_questions(db, quiz_id)

        redis_data = []
        for question, response in zip(db_questions, responses):
            redis_response = QuizResponseRedis(
                selected_answers=response.selected_answers,
                is_correct=sorted(question.correct_answers) == sorted(response.selected_answers),
            )
            redis_data.append(
                {
                    "question_text": question.text,
                    "question_answer_options": question.answer_options,
                    "response": redis_response.model_dump(),
                }
            )

        quiz_data = {
            "quiz_id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "company_id": quiz.company_id,
            "user_id": user_id,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
        }
        redis_data.append({"quiz_data": quiz_data})

        json_data = json.dumps(redis_data)
        await redis_client.setex(key, timedelta(hours=48), json_data)

        logger.info(f"Stored quiz responses for user {user_id}, quiz {quiz_id} in Redis.")

    async def get_last_completion_time(self, db: AsyncSession, user_id: int, quiz_id: int) -> datetime:
        result = await db.execute(
            select(QuizResultModel.completed_at)
            .filter(QuizResultModel.user_id == user_id, QuizResultModel.quiz_id == quiz_id)
            .order_by(QuizResultModel.completed_at.desc())
        )
        last_completion = result.scalars().first()
        return last_completion


quiz_repository = QuizRepository()
