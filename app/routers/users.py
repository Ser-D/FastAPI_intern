from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, add_pagination, paginate
from fastapi_pagination.utils import disable_installed_extensions_check
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.models.users import User
from app.schemas.users import UserSchema, UserUpdateRequest
from app.services.auth import auth_service

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/users", response_model=Page[UserSchema])
async def get_users(db: AsyncSession = Depends(get_database)):
    users = await User.get_all(db, skip=0, limit=100)
    disable_installed_extensions_check()
    return paginate(users)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_database),
    user=Depends(auth_service.get_current_user),
):
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    body: UserUpdateRequest,
    db: AsyncSession = Depends(get_database),
    user=Depends(auth_service.get_current_user),
):
    user = await User.update(db, user_id, **body.dict(exclude_unset=True))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_database),
    user=Depends(auth_service.get_current_user),
):
    user = await User.delete(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return


add_pagination(router)
