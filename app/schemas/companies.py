from typing import Optional

from pydantic import BaseModel, ConfigDict


class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_visible: Optional[bool] = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class CompanyDetail(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    is_visible: Optional[bool] = True

    model_config = ConfigDict(arbitrary_types_allowed=True)
