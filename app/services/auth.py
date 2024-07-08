# import pickle
# from datetime import datetime, timedelta
# from typing import Optional
#
# import redis
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.core.config import logger, settings
#
# # from jose import JWTError, jwt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # SECRET_KEY = config.SECRET_KEY_JWT
    # ALGORITHM = config.ALGORITHM
    # cache = redis.Redis(
    #     host=settings.REDIS_DOMAIN,
    #     port=settings.REDIS_PORT,
    #     db=0,
    #     password=settings.REDIS_PASSWORD,
    # )

    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str):
        return pwd_context.hash(password)
