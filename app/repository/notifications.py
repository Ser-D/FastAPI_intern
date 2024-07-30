from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.core.config import logger
from app.models.notifications import Notification
from app.models.users import User
from app.models.members import Member


class NotificationRepository:
    async def create_quiz_notification(self, db: AsyncSession, company_id: int, quiz_id: int):

        users = await db.execute(
            select(User).join(Member).filter(Member.company_id == company_id)
        )
        users = users.scalars().all()
        for user in users:
            notification = Notification(
                user_id=user.id,
                message=f"New quiz created in company {company_id}, quiz ID: {quiz_id}, created at {datetime.utcnow()}"
            )
            db.add(notification)
        await db.commit()


notification_repo = NotificationRepository()
