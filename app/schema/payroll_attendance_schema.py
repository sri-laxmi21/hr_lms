from pydantic import BaseModel
from datetime import date
from typing import Optional


class PayrollAttendanceBase(BaseModel):
    user_id: int
    month: str  # Format YYYY-MM
    total_days: int
    present_days: int
    half_days: int
    absent_days: int
    gross_salary: float
    net_salary: float
    status: Optional[str] = "Generated"


class PayrollAttendanceCreate(PayrollAttendanceBase):
    pass


class PayrollAttendanceUpdate(BaseModel):
    total_days: Optional[int] = None
    present_days: Optional[int] = None
    half_days: Optional[int] = None
    absent_days: Optional[int] = None
    gross_salary: Optional[float] = None
    net_salary: Optional[float] = None
    status: Optional[str] = None


class PayrollAttendanceResponse(PayrollAttendanceBase):
    id: int
    generated_on: Optional[date]

    model_config = {
    "from_attributes": True
}

