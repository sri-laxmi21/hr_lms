from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# --------------------- CREATE ---------------------
class ShiftRosterDetailCreate(BaseModel):
    shift_roster_id: int
    week_day_id: int
    shift_id: int


# --------------------- UPDATE ---------------------
class ShiftRosterDetailUpdate(BaseModel):
    week_day_id: Optional[int] = None
    shift_id: Optional[int] = None


# --------------------- RESPONSE ---------------------
class ShiftRosterDetailResponse(BaseModel):
    id: int
    shift_roster_id: int
    week_day_id: int
    shift_id: int

    # Added based on your request
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None        # STRING ✔
    modified_by: Optional[str] = None       # STRING ✔

    model_config = {"from_attributes": True}
