from datetime import datetime, timedelta

from sqlalchemy.future import select

from app.db.postgres import get_database
from app.models.members import Member
from app.models.quiz import Quiz
from app.models.users import User
from app.repository.notifications import notification_repo
from app.repository.quizzes import quiz_repository


async def fetch_quizzes(db):
    result = await db.execute(select(Quiz))
    return result.scalars().all()


async def fetch_members(db, company_id):
    result = await db.execute(select(Member).filter(Member.company_id == company_id))
    return result.scalars().all()


async def fetch_user(db, user_id):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()


async def check_quiz_completions():
    async for db in get_database():
        try:
            quizzes = await fetch_quizzes(db)
            for quiz in quizzes:
                members = await fetch_members(db, quiz.company_id)
                for member in members:
                    user = await fetch_user(db, member.user_id)
                    if not user:
                        continue

                    last_completion_time = await quiz_repository.get_last_completion_time(db, user.id, quiz.id)
                    if not last_completion_time or (datetime.utcnow() - last_completion_time > timedelta(hours=24)):
                        await notification_repo.create_incomplete_quiz_notification(db, user.id, quiz.id)
        finally:
            await db.close()
