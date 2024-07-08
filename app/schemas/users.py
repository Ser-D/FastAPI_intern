import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    class Config:
        orm_mode = True


class SignInRequest(BaseModel):
    email: str
    password: str


class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("email")
    def email_cheacker(cls, value_email):
        if re.search(r"[\w.-]+@[\w.-]+", value_email):
            return value_email
        raise ValueError("Invalid email")


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator("email")
    def email_cheacker(cls, value_email):
        if re.search(r"[\w.-]+@[\w.-]+", value_email):
            return value_email
        raise ValueError("Invalid email")


class UsersListResponse(BaseModel):
    users: List[User]

    class Config:
        orm_mode = True


class UserDetailResponse(BaseModel):
    user: User
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
