from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models.company import Company
from app.models.members import Member
from app.models.users import User
from app.repository.members import MemberRepository


@pytest.mark.asyncio
async def test_create_member(mock_db_session, member_data):
    member_repo = MemberRepository()
    member = await member_repo.create_member(db=mock_db_session, member=member_data)
    assert member.user_id == member_data.user_id
    assert mock_db_session.add.called
    assert mock_db_session.commit.called
    assert mock_db_session.refresh.called


@pytest.mark.asyncio
async def test_get_member(mock_db_session, member_data):
    member_repo = MemberRepository()
    member = Member(**member_data.model_dump())

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = member
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db_session.execute.return_value = mock_result

    result = await member_repo.get_member(
        db=mock_db_session,
        user_id=member_data.user_id,
        company_id=member_data.company_id,
    )
    assert result == member
    mock_db_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalars.first.assert_called_once()


@pytest.mark.asyncio
async def test_user_exists(mock_db_session):
    user = User(id=1, email="test@example.com")

    with patch.object(User, "get_by_id", new_callable=AsyncMock, return_value=user) as mock_get_by_id:
        member_repo = MemberRepository()
        result = await member_repo.user_exists(db=mock_db_session, user_id=1)
        assert result is True
        mock_get_by_id.assert_awaited_once_with(mock_db_session, 1)


@pytest.mark.asyncio
async def test_is_owner(mock_db_session):
    company = Company(id=1, owner_id=1)

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = company
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db_session.execute.return_value = mock_result

    member_repo = MemberRepository()
    result = await member_repo.is_owner(db=mock_db_session, user_id=1, company_id=1)
    assert result is True
    mock_db_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalars.first.assert_called_once()


@pytest.mark.asyncio
async def test_update_member_is_admin(mock_db_session, member_data):
    member = Member(**member_data.model_dump())
    member.is_admin = True

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = member
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db_session.execute.return_value = mock_result
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None

    member_repo = MemberRepository()
    result = await member_repo.update_member_is_admin(
        db=mock_db_session,
        user_id=member_data.user_id,
        company_id=member_data.company_id,
        is_admin=True,
    )
    assert result.is_admin is True
    mock_db_session.execute.assert_awaited_once()
    mock_db_session.commit.assert_awaited_once()
    mock_db_session.refresh.assert_awaited_once_with(member)


@pytest.mark.asyncio
async def test_member_exists(mock_db_session, member_data):
    member = Member(**member_data.model_dump())

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = member
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db_session.execute.return_value = mock_result

    member_repo = MemberRepository()
    with pytest.raises(HTTPException):
        await member_repo.member_exists(
            db=mock_db_session,
            user_id=member_data.user_id,
            company_id=member_data.company_id,
        )
    mock_db_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalars.first.assert_called_once()


@pytest.mark.asyncio
async def test_delete_member(mock_db_session, member_data):
    member_repo = MemberRepository()
    member = Member(**member_data.model_dump())

    mock_execute = MagicMock()
    mock_execute.scalars.return_value.first.return_value = member
    mock_db_session.execute = AsyncMock(return_value=mock_execute)
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()

    with patch.object(member_repo, "get_member", AsyncMock(return_value=member)):
        result = await member_repo.delete_member(
            db=mock_db_session,
            user_id=member_data.user_id,
            company_id=member_data.company_id,
        )

        assert result == member
        mock_db_session.delete.assert_awaited_once_with(member)
        mock_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_members(mock_db_session, member_data):
    members = [Member(**member_data.model_dump())]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = members
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db_session.execute.return_value = mock_result

    member_repo = MemberRepository()
    result = await member_repo.get_all_members(db=mock_db_session, company_id=member_data.company_id)
    assert result == members
    mock_db_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalars.all.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_requests_or_invites_by_user(mock_db_session, member_data):
    members = [Member(**member_data.model_dump())]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = members
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db_session.execute.return_value = mock_result

    member_repo = MemberRepository()
    result = await member_repo.get_all_requests_or_invites_by_user(db=mock_db_session, user_id=member_data.user_id)
    assert result == members
    mock_db_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalars.all.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_invited_members(mock_db_session, member_data):
    members = [Member(**member_data.model_dump())]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = members
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db_session.execute.return_value = mock_result

    member_repo = MemberRepository()
    result = await member_repo.get_all_invited_members(db=mock_db_session, owner_id=1)
    assert result == members
    mock_db_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalars.all.assert_called_once()


@pytest.mark.asyncio
async def test_company_exists(mock_db_session):
    company = Company(id=1, name="Test Company", owner_id=1)

    with patch.object(Company, "get_by_id", new_callable=AsyncMock, return_value=company) as mock_get_by_id:
        member_repo = MemberRepository()
        result = await member_repo.company_exists(db=mock_db_session, company_id=1)
        assert result is True
        mock_get_by_id.assert_awaited_once_with(mock_db_session, 1)


@pytest.mark.asyncio
async def test_accept_membership_request(mock_db_session, member_data):
    member = Member(**member_data.model_dump())
    member.status = "pending"

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = member
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db_session.execute.return_value = mock_result
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = member

    member_repo = MemberRepository()
    result = await member_repo.accept_membership_request(
        db=mock_db_session,
        user_id=member_data.user_id,
        company_id=member_data.company_id,
    )

    assert result.status == "active"
    mock_db_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalars.first.assert_called_once()
    mock_db_session.commit.assert_awaited_once()
    mock_db_session.refresh.assert_awaited_once_with(member)


@pytest.mark.asyncio
async def test_accept_invite(mock_db_session, member_data):
    member = Member(**member_data.model_dump())
    member.status = "pending"  # Встановлюємо статус "pending"
    member.type = "invite"  # Встановлюємо тип "invite"

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = member
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db_session.execute.return_value = mock_result
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = member

    member_repo = MemberRepository()
    result = await member_repo.accept_invite(
        db=mock_db_session,
        user_id=member_data.user_id,
        company_id=member_data.company_id,
    )

    assert result.status == "active"
    mock_db_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalars.first.assert_called_once()
    mock_db_session.commit.assert_awaited_once()
    mock_db_session.refresh.assert_awaited_once_with(member)


@pytest.mark.asyncio
async def test_get_memberships_my_company(mock_db_session, member_data):
    members = [Member(**member_data.model_dump())]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = members
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db_session.execute.return_value = mock_result

    member_repo = MemberRepository()
    result = await member_repo.get_memberships_my_company(
        db=mock_db_session,
        user_id=member_data.user_id,
        company_id=member_data.company_id,
    )
    assert result == members
    mock_db_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalars.all.assert_called_once()


@pytest.mark.asyncio
async def test_get_memberships_all_my_companies(mock_db_session, member_data):
    members = [Member(**member_data.model_dump())]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = members
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db_session.execute.return_value = mock_result

    member_repo = MemberRepository()
    result = await member_repo.get_memberships_all_my_companies(db=mock_db_session, user_id=member_data.user_id)
    assert result == members
    mock_db_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalars.all.assert_called_once()
