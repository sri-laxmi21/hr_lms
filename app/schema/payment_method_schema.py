from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ============================================
# Payment Method Schemas
# ============================================

class PaymentMethodBase(BaseModel):
    """Base schema for payment method"""
    payment_gateway: str = Field(..., pattern="^(razorpay|stripe)$")
    method_type: str = Field(..., min_length=1, max_length=50)  # card, upi, netbanking, wallet


class PaymentMethodCreate(PaymentMethodBase):
    """Schema for creating a new payment method"""
    # Card details (if method_type is 'card')
    card_last4: Optional[str] = Field(None, min_length=4, max_length=4)
    card_brand: Optional[str] = Field(None, max_length=20)  # visa, mastercard, amex
    card_expiry_month: Optional[int] = Field(None, ge=1, le=12)
    card_expiry_year: Optional[int] = Field(None, ge=2024)
    
    # UPI details (if method_type is 'upi')
    upi_id: Optional[str] = Field(None, max_length=100)
    
    # Bank details (if method_type is 'netbanking')
    bank_name: Optional[str] = Field(None, max_length=100)
    
    # Gateway specific IDs (set by backend after gateway API call)
    gateway_customer_id: Optional[str] = None
    gateway_payment_method_id: Optional[str] = None


class PaymentMethodUpdate(BaseModel):
    """Schema for updating payment method"""
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class PaymentMethodResponse(PaymentMethodBase):
    """Schema for payment method response"""
    id: int
    organization_id: int
    
    # Card details (masked)
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None
    card_expiry_month: Optional[int] = None
    card_expiry_year: Optional[int] = None
    
    # UPI details
    upi_id: Optional[str] = None
    
    # Bank details
    bank_name: Optional[str] = None
    
    # Status
    is_default: bool
    is_active: bool
    
    # Audit
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class PaymentMethodListResponse(BaseModel):
    """Schema for listing payment methods"""
    payment_methods: list[PaymentMethodResponse]
    default_payment_method_id: Optional[int] = None
