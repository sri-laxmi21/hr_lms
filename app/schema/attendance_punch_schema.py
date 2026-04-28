from pydantic import BaseModel, ConfigDict
from datetime import datetime, date as DateType, time as TimeType
from typing import Optional


# ----------- Base Schema -----------
class AttendancePunchBase(BaseModel):
    bio_id: str
    punch_date: DateType
    punch_time: TimeType
    punch_type: Optional[str] = None   # IN / OUT / NA


# ----------- Create Schema -----------
class AttendancePunchCreate(AttendancePunchBase):
    pass   # created_by is handled internally, not from user input


# ----------- Update Schema -----------
class AttendancePunchUpdate(BaseModel):
    punch_date: Optional[DateType] = None
    punch_time: Optional[TimeType] = None
    punch_type: Optional[str] = None
    # modified_by removed from input as per your requirement


# ----------- Response Schema -----------
class AttendancePunchResponse(BaseModel):
    id: int

    bio_id: str
    punch_date: DateType
    punch_time: TimeType
    punch_type: Optional[str]

    # >>> Audit Fields Only in Response <<<
    created_by: Optional[str]
    modified_by: Optional[str]

    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
