import pickle
from datetime import datetime, timedelta
from typing import Optional

import redis
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger, settings
from app.db.postgres import get_database
from app.models.users import User


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.SECRET_KEY_JWT
    ALGORITHM = settings.ALGORITHM
    ALGORITHM_ = settings.ALGORITHM_AUTH0
    AUDIENCE = settings.AUDIENCE
    ISSUER = settings.ISSUER
    cache = redis.Redis(
        host=settings.REDIS_DOMAIN,
        port=settings.REDIS_PORT,
        db=0,
        password=settings.REDIS_PASSWORD,
    )
    token_auth_scheme = HTTPBearer()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def create_user(self, db: AsyncSession, **data):
        try:
            new_user = await User.create(db, **data)
            return new_user
        except IntegrityError as e:
            if "duplicate" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
                )
            raise e

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> User:
        user = await User.get_user_by_email(db, email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        if not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        return user

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
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
        token: str = Depends(token_auth_scheme),
        db: AsyncSession = Depends(get_database),
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        logger.info(token)
        if len(token.credentials) > 220:
            email = await self.check_token_auth0(token.credentials, db)
        else:
            try:
                payload = jwt.decode(
                    token.credentials, self.SECRET_KEY, algorithms=[self.ALGORITHM]
                )
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

    async def check_token_auth0(self, token: str, db: AsyncSession) -> str:
        try:
            key = self.load_public_key_from_cert("certificate.pem")

            payload = jwt.decode(
                token,
                key,
                algorithms=[self.ALGORITHM_],
                audience=self.AUDIENCE,
                issuer=self.ISSUER,
            )

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
            return user.email

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    @staticmethod
    def load_public_key_from_cert(cert_path: str):
        with open(cert_path, "rb") as cert_file:
            cert_data = cert_file.read()
        cert = load_pem_x509_certificate(cert_data, default_backend())
        public_key = cert.public_key()
        return public_key


auth_service = Auth()
