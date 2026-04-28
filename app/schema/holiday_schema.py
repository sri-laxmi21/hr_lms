from pydantic import BaseModel, ConfigDict
from datetime import date, datetime


# ---------- Base ----------
class HolidayBase(BaseModel):
    date: date
    name: str | None = None


# ---------- Request Schemas ----------
class HolidayCreate(HolidayBase):
    pass  # created_by will be auto-filled in API, not accepted from user


class HolidayUpdate(BaseModel):
    date: datetime | None = None
    name: str | None = None


# ---------- Response Schema ----------
class HolidayResponse(HolidayBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    modified_by: str | None = None

model_config = ConfigDict(from_attributes=True)
