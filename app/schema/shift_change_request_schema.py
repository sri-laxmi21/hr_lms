# app/schema/shift_change_request_schema.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from app.models.shift_change_request_m import RequestStatus


class ShiftChangeRequestBase(BaseModel):
    user_id: int
    old_shift_id: Optional[int] = None
    new_shift_id: int
    request_date: date
    reason: Optional[str] = None
    status: Optional[RequestStatus] = RequestStatus.Pending

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )


class ShiftChangeRequestCreate(ShiftChangeRequestBase):
    pass


class ShiftChangeRequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None
    reason: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )


class ShiftChangeRequestResponse(ShiftChangeRequestBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )
