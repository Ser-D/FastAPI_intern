from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import logger
from app.models.members import Member
from app.models.notifications import Notification
from app.models.users import User


class NotificationRepository:
    async def create_quiz_notification(
        self, db: AsyncSession, company_id: int, quiz_id: int
    ):
        users = await db.execute(
            select(User).join(Member).filter(Member.company_id == company_id)
        )
        users = users.scalars().all()
        for user in users:
            notification = Notification(
                user_id=user.id,
                message=f"New quiz in company {company_id}, quiz ID: {quiz_id}, created at {datetime.utcnow()}",
            )
            db.add(notification)
        await db.commit()

    async def create_incomplete_quiz_notification(
        self, db: AsyncSession, user_id: int, quiz_id: int
    ):
        logger.info(f"Creating notification for user {user_id} and quiz {quiz_id}")
        message = f"Please complete the quiz with ID {quiz_id}. You have not completed it in the last 24 hours."
        notification = Notification(
            user_id=user_id, message=message, created_at=datetime.utcnow()
        )
        db.add(notification)
        await db.commit()
        logger.info(f"Notification created for user {user_id} for quiz {quiz_id}")


notification_repo = NotificationRepository()
