from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


# 1. User schema
class UserBase(BaseModel):
    username: str
    email: EmailStr
    info: Optional[str] = None


class UserDetailResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# 2. SignIn Request model
class UserSignIn(BaseModel):
    email: EmailStr
    password: str


# 3. SignUp Request model
class UserSignUp(UserBase):
    password: str


# 4. UserUpdate Request model
class UserUpdate(UserBase):
    password: Optional[str] = None


# 5. UsersList Response
class UsersListResponse(BaseModel):
    users: List[UserDetailResponse]
    total: int
