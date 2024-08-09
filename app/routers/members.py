from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.models.users import User
from app.repository.members import member_repository
from app.schemas.members import MemberDetail
from app.services.auth import auth_service

router = APIRouter(prefix="/{company_id}/members", tags=["members"])


@router.get("/view", response_model=list[MemberDetail])
async def membership_company(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
    type: str = Query(None, description="Type of membership: invite or request"),
    status: str = Query(None, description="Status of membership: active or pending"),
):
    await member_repository.is_owner(db, current_user.id, company_id)
    memberships = await member_repository.get_memberships_my_company(db, current_user.id, company_id, type, status)
    return memberships


@router.post("/accept_request", response_model=MemberDetail)
async def accept_request(
    user_id: int,
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await member_repository.is_owner(db, current_user.id, company_id)
    accepted_member = await member_repository.accept_membership_request(db, user_id, company_id)
    return accepted_member


@router.get("/admins", response_model=list[MemberDetail])
async def get_admins(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await member_repository.is_owner(db, current_user.id, company_id)
    admins = await member_repository.get_admins(db, company_id)
    return admins


@router.post("/assign_admin", response_model=MemberDetail)
async def assign_admin(
    company_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await member_repository.is_owner(db, current_user.id, company_id)
    admin_member = await member_repository.assign_admin(db, user_id, company_id)
    return admin_member


@router.post("/remove_admin", response_model=MemberDetail)
async def remove_admin(
    company_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await member_repository.is_owner(db, current_user.id, company_id)
    non_admin_member = await member_repository.remove_admin(db, user_id, company_id)
    return non_admin_member

