from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import messages
from app.db.postgres import get_database
from app.models.users import User
from app.repository.members import member_repository
from app.schemas.members import MemberDetail
from app.schemas.users import (
    LogoutResponse,
    SignInRequest,
    SignUpRequest,
    TokenSchema,
    UserDetailResponse,
    UserSchema,
)
from app.services.auth import auth_service

router = APIRouter()
get_refresh_token = HTTPBearer()


@router.get("/me", response_model=UserDetailResponse)
async def read_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.get("/me/requests", response_model=list[MemberDetail])
async def get_my_requests(
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    return await member_repository.get_all_requests_or_invites_by_user(
        db, current_user.id, type="request"
    )


@router.get("/me/invites", response_model=list[MemberDetail])
async def get_my_invites(
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(auth_service.get_current_user),
):
    return await member_repository.get_all_requests_or_invites_by_user(
        db, current_user.id, type="invite"
    )


@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def signup(body: SignUpRequest, db: AsyncSession = Depends(get_database)):
    data = body.model_dump()
    data["hashed_password"] = auth_service.get_password_hash(data.pop("password1"))
    data.pop("password2", None)
    new_user = await auth_service.create_user(db, **data)
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(
    body: SignInRequest,
    db: AsyncSession = Depends(get_database),
):
    user = await auth_service.authenticate_user(db, body.email, body.password)

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await User.update_token(user.id, refresh_token, db)
    return TokenSchema(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
    db: AsyncSession = Depends(get_database),
):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await User.get_user_by_email(db, email)

    if user.refresh_token != token:
        await User.update_token(None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_CREDENTIALS,
        )

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await User.update_token(user.id, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/logout", response_model=LogoutResponse, status_code=status.HTTP_202_ACCEPTED
)
async def logout(
    user=Depends(auth_service.get_current_user),
    db=Depends(get_database),
):
    user.refresh_token = None
    await db.commit()

    return {"result": "Logout success"}
