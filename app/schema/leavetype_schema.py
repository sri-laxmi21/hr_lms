from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# -------- BASE --------
class LeaveTypeBase(BaseModel):
    leave_type: str
    short_code: str
    is_active: bool = True


# -------- CREATE --------
class LeaveTypeCreate(LeaveTypeBase):
    pass


# -------- UPDATE --------
class LeaveTypeUpdate(BaseModel):
    leave_type: Optional[str] = None
    short_code: Optional[str] = None
    is_active: Optional[bool] = None
   


# -------- RESPONSE --------
class LeaveTypeResponse(LeaveTypeBase):
    id: int

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
