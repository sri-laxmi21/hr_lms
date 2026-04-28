from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ----------------------- BASE -----------------------
class ShiftRosterBase(BaseModel):
    name: str
    is_active: bool = True


# ----------------------- CREATE -----------------------
# No audit fields here (handled automatically in API)
class ShiftRosterCreate(ShiftRosterBase):
    pass


# ----------------------- UPDATE -----------------------
# Only fields allowed to update
class ShiftRosterUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


# ----------------------- RESPONSE -----------------------
# Here we show all audit fields + timestamps
class ShiftRosterResponse(ShiftRosterBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    created_by: Optional[str] = None     # string (✔ as you asked)
    modified_by: Optional[str] = None    # string (✔ as you asked)

    model_config = {
        "from_attributes": True
    }
