from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FormulaBase(BaseModel):
    component_code: str
    component_name: str
    formula_expression: str  
    formula_type: Optional[str] = "earning"
    is_active: Optional[bool] = True
    description: Optional[str] = None
    salary_structure_id: Optional[int] = None


class FormulaCreate(FormulaBase):
    pass


class FormulaUpdate(BaseModel):
    component_code: Optional[str] = None
    component_name: Optional[str] = None
    formula_expression: Optional[str] = None  
    formula_type: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    salary_structure_id: Optional[int] = None


class FormulaResponse(FormulaBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: str | None = None
    modified_by: str | None = None

    model_config = {
    "from_attributes": True
}

