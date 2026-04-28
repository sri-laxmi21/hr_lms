from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.schema.module_schema import ModuleOut


class SubscriptionPlanBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    
    # Pricing
    price_monthly: Decimal = Field(..., ge=0)
    price_yearly: Optional[Decimal] = Field(None, ge=0)
    
    # Limits
    branch_limit: int = Field(default=2, ge=1)
    user_limit: int = Field(default=10, ge=1)
    storage_limit_mb: int = Field(default=1000, ge=100)
    
    # Features
    has_analytics: bool = False
    has_api_access: bool = False
    has_priority_support: bool = False
    has_whatsapp_notifications: bool = False
    has_custom_branding: bool = False
    
    is_active: bool = True
    display_order: int = 0


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Schema for creating a new subscription plan"""
    pass


class SubscriptionPlanUpdate(BaseModel):
    """Schema for updating subscription plan (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    
    # Pricing
    price_monthly: Optional[Decimal] = Field(None, ge=0)
    price_yearly: Optional[Decimal] = Field(None, ge=0)
    
    # Limits
    branch_limit: Optional[int] = Field(None, ge=1)
    user_limit: Optional[int] = Field(None, ge=1)
    storage_limit_mb: Optional[int] = Field(None, ge=100)
    
    # Features
    has_analytics: Optional[bool] = None
    has_api_access: Optional[bool] = None
    has_priority_support: Optional[bool] = None
    has_whatsapp_notifications: Optional[bool] = None
    has_custom_branding: Optional[bool] = None
    
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class SubscriptionPlanResponse(SubscriptionPlanBase):
    """Schema for subscription plan response"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    modules: List[ModuleOut] = []
    
    model_config = {"from_attributes": True}


class SubscriptionPlanPublicResponse(BaseModel):
    """Public schema for pricing page (no admin fields)"""
    id: int
    name: str
    description: Optional[str] = None
    
    # Pricing
    price_monthly: Decimal
    price_yearly: Optional[Decimal] = None
    
    # Limits
    branch_limit: int
    user_limit: int
    storage_limit_mb: int
    
    # Features
    has_analytics: bool
    has_api_access: bool
    has_priority_support: bool
    has_whatsapp_notifications: bool
    has_custom_branding: bool
    modules: List[ModuleOut] = []
    
    # Calculated fields
    @property
    def monthly_savings(self) -> Optional[Decimal]:
        """Calculate monthly savings if paying yearly"""
        if self.price_yearly and self.price_monthly > 0:
            yearly_if_monthly = self.price_monthly * 12
            savings = yearly_if_monthly - self.price_yearly
            return round(savings / 12, 2)
        return None
    
    @property
    def yearly_savings_percentage(self) -> Optional[int]:
        """Calculate savings percentage for yearly plan"""
        if self.price_yearly and self.price_monthly > 0:
            yearly_if_monthly = self.price_monthly * 12
            if yearly_if_monthly > 0:
                savings = ((yearly_if_monthly - self.price_yearly) / yearly_if_monthly) * 100
                return round(savings)
        return None
    
    model_config = {"from_attributes": True}


class PlanComparisonResponse(BaseModel):
    """Schema for comparing multiple plans"""
    plan_id: int
    plan_name: str
    price_monthly: Decimal
    
    features: dict = {
        "branches": int,
        "users": int,
        "storage_gb": float,
        "analytics": bool,
        "api_access": bool,
        "priority_support": bool,
        "whatsapp_notifications": bool,
        "custom_branding": bool
    }
    
    is_current_plan: bool = False
    is_recommended: bool = False