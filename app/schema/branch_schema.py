# app/schema/branch_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BranchBase(BaseModel):
    name: str
    address: Optional[str] = None
    organization_id: int

class BranchCreate(BranchBase):
    pass

class BranchUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    organization_id: Optional[int]

class BranchResponse(BranchBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
    "from_attributes": True
}
 # ✅ Needed for from_orm()
