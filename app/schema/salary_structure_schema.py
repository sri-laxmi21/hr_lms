from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

# ------------------ Base Schema ------------------
class SalaryStructureBase(BaseModel):
    basic_salary_annual: float
    allowances_annual: Optional[float] = 0.0
    deductions_annual: Optional[float] = 0.0
    bonus_annual: Optional[float] = 0.0
    effective_from: date
    effective_to: Optional[date] = None
    is_active: Optional[bool] = True

# ------------------ Create Schema ------------------
class SalaryStructureCreate(SalaryStructureBase):
    pass

# ------------------ Update Schema ------------------
class SalaryStructureUpdate(BaseModel):
    basic_salary_annual: Optional[float] = None
    allowances_annual: Optional[float] = None
    deductions_annual: Optional[float] = None
    bonus_annual: Optional[float] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    is_active: Optional[bool] = None

# ------------------ Response Schema ------------------
class SalaryStructureResponse(SalaryStructureBase):
    id: int
    total_annual: Optional[float] = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str | None = None
    modified_by: str | None = None


    model_config = {
    "from_attributes": True
}

