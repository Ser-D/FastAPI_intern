from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.models.company import Company
from app.models.users import User
from app.schemas.companies import CompanyCreate, CompanyDetail, CompanyUpdate
from app.services.auth import auth_service

router = APIRouter(prefix="/company", tags=["company"])


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
    company = await Company.get_by_id(db=db, company_id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    company = await Company.update(db=db, company_id=company_id, **company_in.dict())
    return company


@router.delete("/{company_id}", response_model=CompanyDetail)
async def delete_company(
    *,
    db: AsyncSession = Depends(get_database),
    company_id: int,
    current_user: User = Depends(auth_service.get_current_user),
) -> CompanyDetail:
    company = await Company.get_by_id(db=db, company_id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    company = await Company.delete(db=db, company_id=company_id)
    return company
