from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, add_pagination, paginate
from fastapi_pagination.utils import disable_installed_extensions_check
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.models.users import User
from app.repository.members import member_repository
from app.schemas.members import MemberCreate, MemberDetail
from app.schemas.users import UserSchema, UserUpdateRequest
from app.services.auth import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/users", response_model=Page[UserSchema])
async def get_users(db: AsyncSession = Depends(get_database)):
    users = await User.get_all(db, skip=0, limit=100)
    disable_installed_extensions_check()
    return paginate(users)


@router.post("/{user_id}/invite", response_model=MemberDetail)
async def invite_user(
    user_id: int,
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await member_repository.user_exists(db, user_id)
    await member_repository.is_owner(db, current_user.id, company_id)
    await member_repository.member_exists(db, user_id, company_id)
    member_create = MemberCreate(
        company_id=company_id,
        user_id=user_id,
        is_admin=False,
        status="pending",
        type="invite",
    )
    return await member_repository.create_member(db, member_create)


@router.post("/{user_id}/remove", response_model=MemberDetail)
async def remove_user(
    user_id: int,
    company_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    await member_repository.is_owner(db, current_user.id, company_id)

    await member_repository.get_member(db, user_id, company_id)

    deleted_member = await member_repository.delete_member(db, user_id, company_id)
    return deleted_member


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_database),
    user=Depends(auth_service.get_current_user),
):
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    body: UserUpdateRequest,
    db: AsyncSession = Depends(get_database),
    user=Depends(auth_service.get_current_user),
):
    if user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile",
        )

    data = body.model_dump()
    data["hashed_password"] = auth_service.get_password_hash(data.pop("password1"))
    data.pop("password2", None)
    user = await User.update(db, user_id, **data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_database),
    user=Depends(auth_service.get_current_user),
):
    if user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own profile",
        )
    user = await User.delete(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return


add_pagination(router)
