# app/schema/permission_schema.py
from pydantic import BaseModel
from datetime import date, datetime, time
from typing import Optional


# ---------------------- BASE ----------------------
class PermissionBase(BaseModel):
    date: date
    reason: Optional[str] = None
    from_time: Optional[time] = None
    to_time: Optional[time] = None


# ---------------------- CREATE ----------------------
class PermissionCreate(PermissionBase):
    user_id: int
    shift_id: int   # Manager selects shift


# ---------------------- UPDATE ----------------------
class PermissionUpdate(BaseModel):
    status: Optional[str] = None   # pending / approved / cancelled
    reason: Optional[str] = None
    from_time: Optional[time] = None
    to_time: Optional[time] = None


# ---------------------- RESPONSE ----------------------
class PermissionResponse(PermissionBase):
    id: int
    user_id: int
    shift_id: int
    status: str

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    created_by: Optional[str] = None   # ✔ String
    modified_by: Optional[str] = None  # ✔ String

    model_config = {
        "from_attributes": True
    }
