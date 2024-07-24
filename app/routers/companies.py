from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.models.company import Company
from app.models.users import User
from app.repository.members import member_repository
from app.schemas.companies import CompanyCreate, CompanyDetail, CompanyUpdate
from app.schemas.members import MemberCreate, MemberDetail
from app.services.auth import auth_service

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanyDetail)
async def create_company(
    *,
    db: AsyncSession = Depends(get_database),
    company_in: CompanyCreate,
    current_user: User = Depends(auth_service.get_current_user),
) -> CompanyDetail:
    company = await Company.create_with_owner(
        db=db, **company_in.dict(), owner_id=current_user.id
    )
    member_create = MemberCreate(
        company_id=company.id,
        user_id=current_user.id,
        is_admin=True,
        status="active",
        type="auto",
    )
    await member_repository.create_member(db, member_create)
    return company


@router.get("/", response_model=List[CompanyDetail])
async def get_all_companies(
    db: AsyncSession = Depends(get_database),
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(auth_service.get_current_user),
) -> List[CompanyDetail]:
    companies = await Company.get_all(db, skip=skip, limit=limit)
    return companies


@router.get("/my_companies", response_model=List[CompanyDetail])
async def get_my_companies(
    db: AsyncSession = Depends(get_database),
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(auth_service.get_current_user),
) -> List[CompanyDetail]:
    companies = await Company.get_all_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return companies


@router.get("/memberships/all", response_model=list[MemberDetail])
async def membership_all_companies(
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
    type: str = Query(None, description="Type of membership: invite or request"),
    status: str = Query(None, description="Status of membership: active or pending"),
):
    memberships = await member_repository.get_memberships_all_my_companies(
        db, current_user.id, type, status
    )
    return memberships


@router.get("/memberships/company/{company_id}", response_model=list[MemberDetail])
async def membership_company(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
    type: str = Query(None, description="Type of membership: invite or request"),
    status: str = Query(None, description="Status of membership: active or pending"),
):
    await member_repository.is_owner(db, current_user.id, company_id)
    memberships = await member_repository.get_memberships_company(
        db, current_user.id, company_id, type, status
    )
    return memberships


@router.post("/{company_id}/join", response_model=MemberDetail)
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


@router.post("/{company_id}/accept-invite", response_model=MemberDetail)
async def accept_invite(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    accepted_member = await member_repository.accept_invite(
        db, current_user.id, company_id
    )
    return accepted_member


@router.post("/{company_id}/leave", response_model=MemberDetail)
async def leave_company(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    member = await member_repository.get_member(db, current_user.id, company_id)

    deleted_member = await member_repository.delete_member(
        db, current_user.id, company_id
    )
    return deleted_member


@router.get("/{company_id}", response_model=CompanyDetail)
async def read_company(
    *,
    db: AsyncSession = Depends(get_database),
    company_id: int,
    current_user: User = Depends(auth_service.get_current_user),
) -> CompanyDetail:
    company = await Company.get_by_id(db=db, company_id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=CompanyDetail)
async def update_company(
    *,
    db: AsyncSession = Depends(get_database),
    company_id: int,
    company_in: CompanyUpdate,
    current_user: User = Depends(auth_service.get_current_user),
) -> CompanyDetail:
    company = await Company.update(
        db=db, company_id=company_id, user=current_user.id, **company_in.dict()
    )
    return company


@router.delete("/{company_id}", response_model=dict)
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await Company.delete(db, company_id, current_user.id)
    return {"detail": "Company deleted successfully"}
