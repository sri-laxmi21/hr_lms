from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

# ============================================
# Payment Processing Schemas
# ============================================

class PaymentInitiateRequest(BaseModel):
    """Schema for initiating a payment"""
    plan_id: int = Field(..., gt=0)
    billing_cycle: str = Field(..., pattern="^(monthly|yearly)$")
    payment_method_id: Optional[int] = None  # If not provided, will use default


class PaymentInitiateResponse(BaseModel):
    """Schema for payment initiation response"""
    order_id: str
    amount: Decimal
    currency: str
    payment_gateway: str
    gateway_order_id: str
    gateway_key_id: Optional[str] = None  # Razorpay key for frontend
    
    # Additional gateway-specific data
    checkout_url: Optional[str] = None  # For hosted checkout pages


class PaymentVerifyRequest(BaseModel):
    """Schema for verifying payment"""
    gateway_payment_id: str
    gateway_order_id: str
    gateway_signature: str


class PaymentVerifyResponse(BaseModel):
    """Schema for payment verification response"""
    success: bool
    payment_id: int
    message: str
    subscription_activated: bool = False


class PaymentResponse(BaseModel):
    """Schema for payment details response"""
    id: int
    organization_id: int
    amount: Decimal
    currency: str
    payment_type: str
    payment_method: Optional[str] = None
    billing_cycle: Optional[str] = None
    
    payment_gateway: Optional[str] = None
    gateway_payment_id: Optional[str] = None
    gateway_order_id: Optional[str] = None
    transaction_id: Optional[str] = None
    
    payment_status: str
    payment_date: Optional[date] = None
    description: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class PaymentHistoryResponse(BaseModel):
    """Schema for payment history"""
    payments: list[PaymentResponse]
    total_payments: int
    total_amount_paid: Decimal


class WebhookPayload(BaseModel):
    """Schema for webhook payload (generic)"""
    event: str
    payload: dict
    signature: Optional[str] = None
