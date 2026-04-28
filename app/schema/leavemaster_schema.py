from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


# ================= BASE =================
class LeaveMasterBase(BaseModel):
    leave_type_id: int
    start_date: date
    end_date: date
    is_half_day: Optional[bool] = False


# ================= CREATE (ORG INCHARGE / ADMIN) =================
class LeaveMasterCreate(LeaveMasterBase):
    user_id: int   # ✅ REQUIRED (leave created for another user)


# ================= UPDATE (Admin) =================
class LeaveMasterUpdate(BaseModel):
    status: str  # approved / rejected / cancelled


# ================= RESPONSE =================
class LeaveMasterResponse(BaseModel):
    id: int
    user_id: int
    leave_type_id: int

    start_date: date
    end_date: date
    leave_days: float
    is_half_day: bool

    status: str

    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str] = None
    modified_by: Optional[str] = None    

    model_config = {
        "from_attributes": True
    }
