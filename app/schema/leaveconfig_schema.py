from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# -------- BASE --------
class LeaveConfigBase(BaseModel):
    leave_type_id: int
    per_month: int
    no_of_leaves: int
    carry_forward: bool = False   # Boolean now

# -------- CREATE --------
class LeaveConfigCreate(LeaveConfigBase):
    pass


# -------- UPDATE --------
class LeaveConfigUpdate(BaseModel):
    leave_type_id: Optional[int] = None
    per_month: Optional[int] = None
    no_of_leaves: Optional[int] = None
    carry_forward: Optional[bool] = None

   


# -------- RESPONSE --------
class LeaveConfigResponse(LeaveConfigBase):
    id: int

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
