from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger
from app.models.users import User
from app.schemas.users import SignUpRequest, UserUpdateRequest


async def get_user_by_email(email: str, db: AsyncSession):
    stmt = select(User).filter_by(email=email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def create_user(body: SignUpRequest, db: AsyncSession):
    new_user = User(
        email=body.email,
        firstname=body.firstname,
        lastname=body.lastname,
        city=body.city,
        phone=body.phone,
        avatar=body.avatar,
        hashed_password=body.password1,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    logger.info(f"Created new user: {new_user.id}")
    return new_user


async def get_user_by_id(user_id: int, db: AsyncSession):
    stmt = select(User).filter_by(id=user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_users(skip: int, limit: int, db: AsyncSession) -> list[User]:
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users


async def update_user(user_id: int, body: UserUpdateRequest, db: AsyncSession):
    stmt = select(User).filter_by(id=user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        if body.email is not None:
            user.email = body.email
        if body.firstname is not None:
            user.firstname = body.firstname
        if body.lastname is not None:
            user.lastname = body.lastname
        if body.city is not None:
            user.city = body.city
        if body.phone is not None:
            user.phone = body.phone
        if body.avatar is not None:
            user.avatar = body.avatar
        await db.commit()
        await db.refresh(user)
        logger.info(f"Updated user: {user.id}")
    return user


async def delete_user(user_id: int, db: AsyncSession):
    user = await get_user_by_id(user_id, db)
    if user:
        await db.delete(user)
        await db.commit()
        logger.info(f"Deleted user: {user.id}")
    return user
