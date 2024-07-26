from pydantic import BaseModel, ConfigDict


class MemberCreate(BaseModel):
    company_id: int
    user_id: int
    is_admin: bool = False
    status: str = "pending"
    type: str


class MemberDetail(BaseModel):
    id: int
    company_id: int
    user_id: int
    is_admin: bool = False
    status: str = "pending"
    type: str

    model_config = ConfigDict(arbitrary_types_allowed=True)
