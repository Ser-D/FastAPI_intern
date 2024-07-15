import json
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx
import redis
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jose import JWTError, jwk, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger, settings
from app.db.postgres import get_database
from app.models.users import User


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.SECRET_KEY_JWT
    ALGORITHM = settings.ALGORITHM
    cache = redis.Redis(
        host=settings.REDIS_DOMAIN,
        port=settings.REDIS_PORT,
        db=0,
        password=settings.REDIS_PASSWORD,
    )
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
    token_auth_scheme = HTTPBearer()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_database),
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user_hash = str(email)
        user = self.cache.get(user_hash)

        if user is None:
            user = await User.get_user_by_email(db, email)
            if user is None:
                raise credentials_exception
            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 300)
        else:
            user = pickle.loads(user)
        return user

    async def decode_refresh_token(self, refresh_token: str) -> str:
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user_auth0(
        self,
        token: HTTPAuthorizationCredentials = Security(token_auth_scheme),
        db: AsyncSession = Depends(get_database),
    ):
        try:
            payload = self.decode_token(token.credentials)
            logger.info(f"Payload: {payload}")

            email = payload.get("email")

            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email not found in token",
                )

            user = await User.get_user_by_email(db, email)
            if not user:
                hashed_password = self.get_password_hash(email)
                user = await User.create(
                    db,
                    firstname="user",
                    lastname="token",
                    email=email,
                    hashed_password=hashed_password,
                    is_active=True,
                )

            logger.info(f"User: {user}")
            access_token = await self.create_access_token(data={"sub": user.email})
            refresh_token = await self.create_refresh_token(data={"sub": user.email})
            await User.update_token(refresh_token, db)
            return {
                "user": user,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.get_unverified_claims(token)
            return payload
        except JWTError as e:
            raise ValueError(f"Invalid token: {e}")


auth_service = Auth()
