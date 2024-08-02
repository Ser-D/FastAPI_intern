# tests/services/test_member_repository.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.member_repository import MemberRepository
from app.schemas.members import MemberCreate
from app.models.members import Member


@pytest.mark.asyncio
async def test_create_member(db_session: AsyncSession):
    repo = MemberRepository()
    member_data = MemberCreate(user_id=1, company_id=1, is_admin=False, status='active', type='request')
    member = await repo.create_member(db_session, member_data)

    assert member.user_id == member_data.user_id
    assert member.company_id == member_data.company_id
    assert member.is_admin == member_data.is_admin
    assert member.status == member_data.status
    assert member.type == member_data.type
