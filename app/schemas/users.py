from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from pydantic_core.core_schema import ValidationInfo

from app.core.config import logger


class UserSchema(BaseModel):
    id: int
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: EmailStr
    city: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SignUpRequest(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: EmailStr
    password1: Optional[str] = "123456"
    password2: Optional[str] = "123456"
    city: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None

    @field_validator("password2")
    def passwords_match(cls, value: str, values: ValidationInfo) -> str:
        if "password1" in values.data and value != values.data["password1"]:
            logger.error("Passwords do not match")
            raise ValueError("Passwords do not match")
        return value


class SignInRequest(BaseModel):
    email: str
    password: str


class UsersListResponse(BaseModel):
    users: List[UserSchema]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UserDetailResponse(BaseModel):
    user: UserSchema
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UserUpdateRequest(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
