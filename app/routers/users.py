from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_database
from app.models.users import User
from app.schemas.users import SignUpRequest, UserSchema, UserUpdateRequest
from app.services.auth import Auth

router = APIRouter()


@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def signup(body: SignUpRequest, db: AsyncSession = Depends(get_database)):
    body.password1 = Auth.get_password_hash(body.password1)
    try:
        new_user = await User.create(
            db,
            email=body.email,
            firstname=body.firstname,
            lastname=body.lastname,
            city=body.city,
            phone=body.phone,
            avatar=body.avatar,
            hashed_password=body.password1,
        )
        return new_user
    except IntegrityError as e:
        if "duplicate" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
            )
        raise e


@router.get("/users", response_model=Page[UserSchema])
async def get_users(db: AsyncSession = Depends(get_database)):
    users = await User.get_all(
        db, skip=0, limit=100
    )  # skip and limit are handled by paginate
    return paginate(users)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: AsyncSession = Depends(get_database)):
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int, body: UserUpdateRequest, db: AsyncSession = Depends(get_database)
):
    user = await User.update(db, user_id, **body.dict(exclude_unset=True))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_database)):
    user = await User.delete(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return


add_pagination(router)
