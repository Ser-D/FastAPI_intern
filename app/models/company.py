from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship

from app.models.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_visible = Column(Boolean, default=True)

    owner = relationship("User", back_populates="companies", collection_class=list)
    members = relationship("Member", back_populates="company", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="company")
    quizzes = relationship("Quiz", back_populates="company")
    quiz_results = relationship("QuizResult", back_populates="company")

    @classmethod
    async def create_with_owner(cls, db: AsyncSession, **kwargs) -> "Company":
        company = cls(**kwargs)
        db.add(company)
        await db.commit()
        await db.refresh(company)
        return company

    @classmethod
    async def get_by_id(cls, db: AsyncSession, company_id: int) -> "Company":
        result = await db.execute(select(cls).filter_by(id=company_id, is_visible=True))
        return result.scalar_one_or_none()

    @classmethod
    async def get_my_company(cls, db: AsyncSession, company_id: int, owner_id: int) -> "Company":
        result = await db.execute(select(cls).filter_by(id=company_id, owner_id=owner_id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, db: AsyncSession, skip: int, limit: int) -> Sequence["Company"]:
        result = await db.execute(select(cls).filter_by(is_visible=True).offset(skip).limit(limit))
        return result.scalars().all()

    @classmethod
    async def get_all_by_owner(cls, db: AsyncSession, owner_id: int, skip: int, limit: int) -> Sequence["Company"]:
        result = await db.execute(select(cls).filter_by(owner_id=owner_id).offset(skip).limit(limit))
        return result.scalars().all()

    @classmethod
    async def get_visible_by_id(cls, db: AsyncSession, company_id: int) -> "Company":
        company = await cls.get_by_id(db, company_id)
        if company is None or not company.is_visible:
            return None
        return company

    @classmethod
    async def update(cls, db: AsyncSession, company_id: int, user: int, **kwargs) -> "Company":
        company = await cls.get_my_company(db, company_id, user)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        for key, value in kwargs.items():
            setattr(company, key, value)
        await db.commit()
        await db.refresh(company)
        return company

    @classmethod
    async def delete(cls, db: AsyncSession, company_id: int, user_id: int) -> "Company":
        company = await cls.get_my_company(db, company_id, user_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        await db.delete(company)
        await db.commit()
        return company
