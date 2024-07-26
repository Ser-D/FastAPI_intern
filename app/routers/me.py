from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.models.users import User
from app.repository.members import member_repository
from app.schemas.members import MemberDetail
from app.schemas.users import UserDetailResponse
from app.services.auth import auth_service

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/", response_model=UserDetailResponse)
async def read_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.get("/requests", response_model=list[MemberDetail])
async def get_my_requests(
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    return await member_repository.get_all_requests_or_invites_by_user(
        db, current_user.id, type="request"
    )


@router.get("/invites", response_model=list[MemberDetail])
async def get_my_invites(
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    return await member_repository.get_all_requests_or_invites_by_user(
        db, current_user.id, type="invite"
    )


@router.post("/invites/{member_id}", response_model=MemberDetail)
async def accept_invite(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    accepted_member = await member_repository.accept_invite(
        db, current_user.id, company_id
    )
    return accepted_member
