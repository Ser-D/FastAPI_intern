from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    created_at: datetime
    status: bool

    class Config:
        from_attributes = True
