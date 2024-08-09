from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(from_attributes=True)
