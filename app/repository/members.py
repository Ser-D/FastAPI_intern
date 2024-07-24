from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.company import Company
from app.models.members import Member
from app.models.users import User
from app.schemas.members import MemberCreate


class MemberRepository:
    async def create_member(self, db: AsyncSession, member: MemberCreate) -> Member:
        member = Member(**member.dict())
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member

    async def get_member(self, db: AsyncSession, user_id: int, company_id: int) -> Member:
        result = await db.execute(
            select(Member).filter_by(user_id=user_id, company_id=company_id)
        )
        member = result.scalars().first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        return member

    async def user_exists(self, db: AsyncSession, user_id: int) -> bool:
        user = await User.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return True

    async def is_owner(self, db: AsyncSession, user_id: int, company_id: int) -> bool:
        result = await db.execute(
            select(Company).filter_by(id=company_id, owner_id=user_id)
        )
        company = result.scalars().first()
        if not company:
            raise HTTPException(status_code=403, detail="Access denied: User is not the owner of the company")
        return True

    async def update_member_is_admin(self, db: AsyncSession, user_id: int, company_id: int, is_admin: bool) -> Member:
        result = await db.execute(
            select(Member).filter_by(user_id=user_id, company_id=company_id)
        )
        member = result.scalars().first()
        if member:
            member.is_admin = is_admin
            await db.commit()
            await db.refresh(member)
        return member

    async def member_exists(self, db: AsyncSession, user_id: int, company_id: int) -> bool:
        result = await db.execute(
            select(Member).filter_by(user_id=user_id, company_id=company_id)
        )
        member = result.scalars().first()
        if member:
            raise HTTPException(status_code=400, detail="Membership or invite already exists")
        return False

    async def delete_member(self, db: AsyncSession, user_id: int, company_id: int) -> Member:
        member = await self.get_member(db, user_id, company_id)
        if member.type == "auto":
            raise HTTPException(status_code=403, detail="You cannot leave the company with auto membership")

        await db.delete(member)
        await db.commit()
        return member

    async def get_all_members(self, db: AsyncSession, company_id: int, skip: int = 0, limit: int = 10) -> Sequence[
        Member]:
        result = await db.execute(
            select(Member).filter_by(company_id=company_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_all_requests_or_invites_by_user(self, db: AsyncSession, user_id: int, type: str = None, skip: int = 0,
                                                  limit: int = 10) -> list[Member]:
        query = select(Member).filter(Member.user_id == user_id)
        if type:
            query = query.filter(Member.type == type)
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_all_invited_members(self,
                                      db: AsyncSession,
                                      owner_id: int,
                                      skip: int = 0,
                                      limit: int = 10
                                      ) -> list[Member]:
        result = await db.execute(
            select(Member)
            .join(Company, Company.id == Member.company_id)
            .filter(Company.owner_id == owner_id, Member.type == 'invite')
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def company_exists(self, db: AsyncSession, company_id: int) -> bool:
        company = await Company.get_by_id(db, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return True

    async def accept_membership_request(self, db: AsyncSession, user_id: int, company_id: int) -> Member:
        member = await self.get_member(db, user_id, company_id)
        if member.status != "pending":
            raise HTTPException(status_code=400, detail="Only pending requests can be accepted")
        member.status = "active"
        await db.commit()
        await db.refresh(member)
        return member

    async def accept_invite(self, db: AsyncSession, user_id: int, company_id: int) -> Member:
        member = await self.get_member(db, user_id, company_id)
        if member.status != "pending" or member.type != "invite":
            raise HTTPException(status_code=400, detail="Only pending invites can be accepted")
        member.status = "active"
        await db.commit()
        await db.refresh(member)
        return member

    async def get_memberships_all_companies(self, db: AsyncSession, user_id: int, type: str = None,
                                            status: str = None) -> list[Member]:
        query = select(Member).filter(Member.user_id == user_id)
        if type:
            query = query.filter(Member.type == type)
        if status:
            query = query.filter(Member.status == status)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_memberships_all_my_companies(self, db: AsyncSession, user_id: int, type: str = None, status: str = None) -> list[Member]:
        query = (
            select(Member)
            .join(Company, Company.id == Member.company_id)
            .filter(Company.owner_id == user_id)
        )
        if type:
            query = query.filter(Member.type == type)
        if status:
            query = query.filter(Member.status == status)
        result = await db.execute(query)
        return result.scalars().all()


member_repository = MemberRepository()
