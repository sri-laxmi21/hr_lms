from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class UserShiftBase(BaseModel):
    user_id: int
    shift_id: int
    assigned_date: date
    is_active: Optional[bool] = True


class UserShiftCreate(UserShiftBase):
    pass


class UserShiftUpdate(BaseModel):
    shift_id: Optional[int] = None
    assigned_date: Optional[date] = None
    is_active: Optional[bool] = None


class UserShiftResponse(BaseModel):
    id: int
    user_id: int
    shift_id: int
    assigned_date: date
    is_active: bool

    # 👉 Added fields
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
