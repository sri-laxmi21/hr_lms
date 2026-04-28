# app/schema/attendance_schema.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


# ---------------------------
# Base Schema
# ---------------------------
class AttendanceSummaryBase(BaseModel):
    user_id: int
    month: date  # stored as first day of the month


# ---------------------------
# Create Schema (internal use)
# ---------------------------
class AttendanceSummaryCreate(AttendanceSummaryBase):
    total_days: int = 0
    present_days: int = 0
    absent_days: int = 0
    half_days: int = 0
    holidays: int = 0
    sundays: int = 0
    leaves: int = 0
    permissions: int = 0

    total_work_minutes: int = 0
    overtime_minutes: int = 0
    late_minutes: int = 0
    early_exit_minutes: int = 0

    summary_status: str = "Pending"


# ---------------------------
# Update Schema (optional)
# ---------------------------
class AttendanceSummaryUpdate(BaseModel):
    total_days: Optional[int] = None
    present_days: Optional[int] = None
    absent_days: Optional[int] = None
    half_days: Optional[int] = None
    holidays: Optional[int] = None
    sundays: Optional[int] = None
    leaves: Optional[int] = None
    permissions: Optional[int] = None

    total_work_minutes: Optional[int] = None
    overtime_minutes: Optional[int] = None
    late_minutes: Optional[int] = None
    early_exit_minutes: Optional[int] = None

    summary_status: Optional[str] = None


# ---------------------------
# Response Schema
# ---------------------------
class AttendanceSummaryResponse(BaseModel):
    id: int
    user_id: int
    month: date

    total_days: int
    present_days: int
    absent_days: int
    half_days: int
    holidays: int
    sundays: int
    leaves: int
    permissions: int

    total_work_minutes: int
    overtime_minutes: int
    late_minutes: int
    early_exit_minutes: int

    summary_status: str

    created_at: datetime
    updated_at: Optional[datetime]

    # ✔ show created_by & modified_by in response only
    created_by: Optional[str]
    modified_by: Optional[str]

    model_config = {"from_attributes": True}
