from collections.abc import Sequence

from sqlalchemy import Boolean, DateTime, Integer, String, func, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    email = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    city = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    refresh_token = Column(String(), nullable=True)

    companies = relationship("Company", back_populates="owner", cascade="all, delete-orphan")
    members = relationship("Member", back_populates="user", cascade="all, delete-orphan")
    quiz_results = relationship("QuizResult", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

    @classmethod
    async def get_user_by_email(cls, db: AsyncSession, email: str):
        result = await db.execute(select(cls).filter_by(email=email))
        return result.scalar_one_or_none()

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        user = cls(**kwargs)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @classmethod
    async def get_by_id(cls, db: AsyncSession, user_id: int):
        result = await db.execute(select(cls).filter_by(id=user_id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, db: AsyncSession, skip: int, limit: int) -> Sequence["User"]:
        result = await db.execute(select(cls).offset(skip).limit(limit))
        return result.scalars().all()

    @classmethod
    async def update(cls, db: AsyncSession, user_id: int, **kwargs):
        user = await cls.get_by_id(db, user_id)
        for key, value in kwargs.items():
            setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
        return user

    @classmethod
    async def delete(cls, db: AsyncSession, user_id: int):
        user = await cls.get_by_id(db, user_id)
        await db.delete(user)
        await db.commit()
        return user

    @classmethod
    async def update_token(cls, user_id: int, token: str | None, db: AsyncSession):
        user = await cls.get_by_id(db, user_id)
        user.refresh_token = token
        await db.commit()
