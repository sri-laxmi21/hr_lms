from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=255)


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization (used during registration)"""
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    plan_id: Optional[int] = None  # If not provided, assign default plan

class OrganizationUpdate(BaseModel):
    """Schema for updating organization details"""
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class OrganizationAdminUpdate(BaseModel):
    """Schema for admin/super-admin to update org settings (includes plan & limits)"""
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=255)
    plan_id: Optional[int] = None
    subscription_status: Optional[str] = Field(None, pattern="^(active|trial|expired|suspended)$")
    subscription_end_date: Optional[date] = None
    
    # Manual limit overrides (for custom deals)
    branch_limit: Optional[int] = Field(None, ge=0)
    user_limit: Optional[int] = Field(None, ge=0)
    storage_limit_mb: Optional[int] = Field(None, ge=0)
    
    is_active: Optional[bool] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    """Basic organization response"""
    id: int
    is_active: bool
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrganizationDetailResponse(OrganizationResponse):
    """Detailed organization response with subscription info"""
    
    # Subscription Info
    plan_id: Optional[int] = None
    subscription_status: str
    subscription_start_date: Optional[date] = None
    subscription_end_date: Optional[date] = None
    
    # Trial Period Info
    is_trial: bool
    trial_start_date: Optional[date] = None
    trial_end_date: Optional[date] = None
    trial_days: int
    
    # Usage Tracking
    branch_limit: int
    current_branches: int
    user_limit: int
    current_users: int
    storage_limit_mb: int
    current_storage_mb: int
    
    # Billing Info
    last_payment_date: Optional[date] = None
    next_billing_date: Optional[date] = None
    total_amount_paid: Decimal
    
    # Calculated fields
    @property
    def branches_remaining(self) -> int:
        return max(0, self.branch_limit - self.current_branches)
    
    @property
    def users_remaining(self) -> int:
        return max(0, self.user_limit - self.current_users)
    
    @property
    def storage_remaining_mb(self) -> int:
        return max(0, self.storage_limit_mb - self.current_storage_mb)
    
    @property
    def is_subscription_active(self) -> bool:
        if not self.subscription_end_date:
            return self.subscription_status in ["active", "trial"]
        return self.subscription_end_date >= date.today() and self.subscription_status in ["active", "trial"]
    
    @property
    def trial_days_remaining(self) -> Optional[int]:
        if not self.is_trial or not self.trial_end_date:
            return None
        remaining = (self.trial_end_date - date.today()).days
        return max(0, remaining)
    
    @property
    def is_trial_expired(self) -> bool:
        if not self.is_trial or not self.trial_end_date:
            return False
        return date.today() > self.trial_end_date

    model_config = {"from_attributes": True}


class OrganizationStatsResponse(BaseModel):
    """Organization statistics for dashboard"""
    organization_id: int
    organization_name: str
    
    total_branches: int
    total_users: int
    total_courses: int
    storage_used_mb: int
    storage_limit_mb: int
    
    subscription_status: str
    days_until_expiry: Optional[int] = None
    plan_name: Optional[str] = None

    model_config = {"from_attributes": True}