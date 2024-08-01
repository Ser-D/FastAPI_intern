from datetime import datetime, timedelta

from sqlalchemy.future import select

from app.db.postgres import get_database
from app.models.members import Member
from app.models.quiz import Quiz
from app.models.users import User
from app.repository.notifications import notification_repo
from app.repository.quizzes import quiz_repository


async def check_quiz_completions():
    db_generator = get_database()
    db = await db_generator.__anext__()
    try:
        quizzes_result = await db.execute(select(Quiz))
        quizzes = quizzes_result.scalars().all()

        for quiz in quizzes:
            company_id = quiz.company_id
            members_result = await db.execute(
                select(Member).filter(Member.company_id == company_id)
            )
            members = members_result.scalars().all()

            for member in members:
                user_result = await db.execute(
                    select(User).filter(User.id == member.user_id)
                )
                user = user_result.scalars().first()

                if not user:
                    continue

                last_completion_time = await quiz_repository.get_last_completion_time(
                    db, user.id, quiz.id
                )
                if not last_completion_time or (
                    datetime.utcnow() - last_completion_time > timedelta(hours=24)
                ):
                    await notification_repo.create_incomplete_quiz_notification(
                        db, user.id, quiz.id
                    )
    finally:
        await db.close()
