from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import messages
from app.db.postgres import get_database
from app.repository import users as repo_users
from app.schemas.users import SignUpRequest, UserSchema, UserUpdateRequest
from app.services.auth import Auth

router = APIRouter(prefix="", tags=[""])


@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def signup(
    body: SignUpRequest,
    bt: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_database),
):
    exist_user = await repo_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST
        )
    body.password1 = Auth.get_password_hash(body.password1)
    new_user = await repo_users.create_user(body, db)
    return new_user


@router.get("/users", response_model=List[UserSchema])
async def get_users(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_database)
):
    users = await repo_users.get_users(skip=skip, limit=limit, db=db)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Users not found"
        )
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_database),
):
    user = await repo_users.get_user_by_id(user_id=user_id, db=db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserUpdateRequest)
async def update_user(
    user_id: int,
    body: UserUpdateRequest,
    db: AsyncSession = Depends(get_database),
):
    user = await repo_users.update_user(user_id=user_id, body=body, db=db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_database),
):
    user = await repo_users.delete_user(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return
