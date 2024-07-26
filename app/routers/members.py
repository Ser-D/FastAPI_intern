from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.models.users import User
from app.repository.members import member_repository
from app.schemas.members import MemberCreate, MemberDetail
from app.services.auth import auth_service

router = APIRouter(prefix="/companies/{company_id}/members", tags=["members"])


@router.get("/view", response_model=list[MemberDetail])
async def membership_company(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
    type: str = Query(None, description="Type of membership: invite or request"),
    status: str = Query(None, description="Status of membership: active or pending"),
):
    await member_repository.is_owner(db, current_user.id, company_id)
    memberships = await member_repository.get_memberships_my_company(
        db, current_user.id, company_id, type, status
    )
    return memberships


@router.post("/accept_request", response_model=MemberDetail)
async def accept_request(
    user_id: int,
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await member_repository.is_owner(db, current_user.id, company_id)
    accepted_member = await member_repository.accept_membership_request(
        db, user_id, company_id
    )
    return accepted_member


@router.post("/join", response_model=MemberDetail)
async def join_company(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await member_repository.company_exists(db, company_id)
    await member_repository.member_exists(db, current_user.id, company_id)

    member_create = MemberCreate(
        company_id=company_id,
        user_id=current_user.id,
        is_admin=False,
        status="pending",
        type="request",
    )
    return await member_repository.create_member(db, member_create)


@router.post("/leave", response_model=MemberDetail)
async def leave_company(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await member_repository.get_member(db, current_user.id, company_id)

    deleted_member = await member_repository.delete_member(
        db, current_user.id, company_id
    )
    return deleted_member
