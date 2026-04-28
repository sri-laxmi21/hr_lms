from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from typing import Optional

class PayrollBase(BaseModel):
    user_id: int
    salary_structure_id: int
    month: str = Field(..., description="Format: YYYY-MM")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "user_id": 1,
                    "salary_structure_id": 3,
                    "month": "2025-10"
                }
            ]
        }
    )

class PayrollCreate(PayrollBase):
    """Backend calculates salary; frontend only sends user + structure + month"""
    pass


# ---------------- Update Schema ----------------
class PayrollUpdate(BaseModel):
    status: Optional[str] = None
    recalculate: Optional[bool] = Field(
        False,
        description="If True, system recalculates salary using latest formulas."
    )

class PayrollResponse(BaseModel):
    id: int
    user_id: int
    salary_structure_id: int
    month: str

    basic_salary: float
    allowances: float
    deductions: float
    bonus: float

    gross_salary: float
    net_salary: float

    status: str
    user_name: Optional[str] = None
    salary_structure_name: Optional[str] = None

    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
