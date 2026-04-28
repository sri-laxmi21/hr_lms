from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ----------------------------
# Base schema (common fields)
# ----------------------------
class NotificationBase(BaseModel):
    message: str
    candidate_id: Optional[int] = None


# ----------------------------
# Create schema (POST)
# ----------------------------
class NotificationCreate(NotificationBase):
    created_by: int  # admin who created the notification
    pass


# ----------------------------
# Update schema (PATCH/PUT)
# ----------------------------
class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


# ----------------------------
# Response schema (GET)
# ----------------------------
class NotificationResponse(BaseModel):
    id: int
    candidate_id: Optional[int]
    created_by: int
    message: str
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True  # was orm_mode in v1
    }
