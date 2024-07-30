from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.quizresult import QuizResult


class QuizResultRepository:
    async def create_quiz_result(
        self,
        db: AsyncSession,
        user_id: int,
        company_id: int,
        quiz_id: int,
        correct_answers: int,
        total_questions: int,
        score: float,
    ) -> QuizResult:
        quiz_result = QuizResult(
            user_id=user_id,
            company_id=company_id,
            quiz_id=quiz_id,
            correct_answers=correct_answers,
            total_questions=total_questions,
            score=score,
        )
        db.add(quiz_result)
        await db.commit()
        await db.refresh(quiz_result)
        return quiz_result

    async def calculate_user_average_score_in_company(
        self, db: AsyncSession, user_id: int, company_id: int
    ):
        result = await db.execute(
            select(
                func.sum(QuizResult.total_questions).label("total_questions"),
                func.sum(QuizResult.correct_answers).label("total_correct_answers"),
            )
            .filter(QuizResult.user_id == user_id)
            .filter(QuizResult.company_id == company_id)
        )
        data = result.fetchone()

        total_questions = data.total_questions or 0
        total_correct_answers = data.total_correct_answers or 0

        percentage = (
            (total_correct_answers / total_questions * 100)
            if total_questions > 0
            else 0
        )

        return {
            "user_id": user_id,
            "company_id": company_id,
            "total_questions": total_questions,
            "total_correct_answers": total_correct_answers,
            "percentage": percentage,
        }

    async def calculate_user_average_score_systemwide(
        self, db: AsyncSession, user_id: int
    ):
        result = await db.execute(
            select(
                func.sum(QuizResult.total_questions).label("total_questions"),
                func.sum(QuizResult.correct_answers).label("total_correct_answers"),
            ).filter(QuizResult.user_id == user_id)
        )
        data = result.fetchone()

        total_questions = data.total_questions or 0
        total_correct_answers = data.total_correct_answers or 0

        percentage = (
            (total_correct_answers / total_questions * 100)
            if total_questions > 0
            else 0
        )

        return {
            "user_id": user_id,
            "total_questions": total_questions,
            "total_correct_answers": total_correct_answers,
            "percentage": percentage,
        }


repo_quizresult = QuizResultRepository()
