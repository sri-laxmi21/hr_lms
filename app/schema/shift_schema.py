from pydantic import BaseModel
from datetime import time, datetime
from typing import Optional


class ShiftBase(BaseModel):
    shift_name: str
    shift_code: str
    shift_type: Optional[str] = None
    start_time: time
    end_time: time
    working_minutes: int
    lag_minutes: Optional[int] = 60
    description: Optional[str] = None
    status: Optional[str] = "active"
    is_week_off: Optional[int] = 0


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(BaseModel):
    shift_name: Optional[str] = None
    shift_code: Optional[str] = None
    shift_type: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    working_minutes: Optional[int] = None
    lag_minutes: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None
    is_week_off: Optional[int] = None


class ShiftResponse(ShiftBase):
    id: int
    created_at: Optional[datetime] = None       # FIX: allow None
    updated_at: Optional[datetime] = None        # ✅ FIXED
    created_by: Optional[int] = None             # integer FK
    modified_by: Optional[str] = None            # string username

    model_config = {"from_attributes": True}
