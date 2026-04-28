from pydantic import BaseModel
from typing import Optional


# ---------- Base ----------
class SubscriptionPlanModuleBase(BaseModel):
    plan_id: int
    module_id: int


# ---------- Create ----------
class SubscriptionPlanModuleCreate(SubscriptionPlanModuleBase):
    pass


# ---------- Update (optional) ----------
class SubscriptionPlanModuleUpdate(BaseModel):
    plan_id: Optional[int] = None
    module_id: Optional[int] = None


# ---------- Response / Read ----------
class SubscriptionPlanModuleOut(SubscriptionPlanModuleBase):
    id: int

    class Config:
        from_attributes = True  # for SQLAlchemy ORM compatibility
