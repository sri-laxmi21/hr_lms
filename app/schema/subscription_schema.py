from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

# ============================================
# Subscription Management Schemas
# ============================================

class SubscriptionUpgradeRequest(BaseModel):
    """Schema for upgrading subscription plan"""
    new_plan_id: int = Field(..., gt=0)
    billing_cycle: str = Field(..., pattern="^(monthly|yearly)$")
    payment_method_id: Optional[int] = None  # If not provided, use default


class SubscriptionDowngradeRequest(BaseModel):
    """Schema for downgrading subscription plan"""
    new_plan_id: int = Field(..., gt=0)
    effective_date: Optional[date] = None  # If not provided, effective immediately


class SubscriptionCancelRequest(BaseModel):
    """Schema for canceling subscription"""
    reason: Optional[str] = Field(None, max_length=500)
    cancel_immediately: bool = False  # If False, cancel at end of billing period


class SubscriptionStatusResponse(BaseModel):
    """Schema for subscription status"""
    organization_id: int
    organization_name: str
    
    # Current Plan
    plan_id: Optional[int] = None
    plan_name: Optional[str] = None
    subscription_status: str
    
    # Dates
    subscription_start_date: Optional[date] = None
    subscription_end_date: Optional[date] = None
    next_billing_date: Optional[date] = None
    
    # Trial Info
    is_trial: bool
    trial_start_date: Optional[date] = None
    trial_end_date: Optional[date] = None
    trial_days_remaining: Optional[int] = None
    
    # Usage
    branch_limit: int
    current_branches: int
    user_limit: int
    current_users: int
    storage_limit_mb: int
    current_storage_mb: int
    
    # Billing
    last_payment_date: Optional[date] = None
    total_amount_paid: Decimal
    
    model_config = {"from_attributes": True}


class TrialStatusResponse(BaseModel):
    """Schema for trial period status"""
    is_trial: bool
    trial_start_date: Optional[date] = None
    trial_end_date: Optional[date] = None
    trial_days_remaining: Optional[int] = None
    trial_expired: bool = False
    can_convert_to_paid: bool = True


class ConvertTrialRequest(BaseModel):
    """Schema for converting trial to paid subscription"""
    plan_id: int = Field(..., gt=0)
    billing_cycle: str = Field(..., pattern="^(monthly|yearly)$")
    payment_method_id: Optional[int] = None


class SubscriptionActionResponse(BaseModel):
    """Generic response for subscription actions"""
    success: bool
    message: str
    subscription_status: Optional[SubscriptionStatusResponse] = None
    payment_required: bool = False
    payment_order_id: Optional[str] = None
