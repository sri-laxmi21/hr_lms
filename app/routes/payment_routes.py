from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from decimal import Decimal

from app.database import get_db
from app.models.user_m import User
from app.models.organization_m import Organization
from app.models.subscription_plans_m import SubscriptionPlan
from app.models.payment_m import Payment
from app.dependencies import get_current_user, require_org_admin
from app.schema.payment_schema import (
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
    PaymentResponse,
    PaymentHistoryResponse,
    WebhookPayload
)
from app.utils.payment_gateway import PaymentGatewayFactory
from app.utils.subscription_manager import SubscriptionManager
from app.utils.webhook_handler import WebhookHandler
from app.config import settings

router = APIRouter(prefix="/payments", tags=["Payments"])


# ============================================
# INITIATE PAYMENT
# ============================================
@router.post("/initiate", response_model=PaymentInitiateResponse)
async def initiate_payment(
    payload: PaymentInitiateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_admin)
):
    """
    Initiate a payment for subscription
    Creates payment order in gateway and returns order details
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization assigned"
        )
    
    org = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    # Get plan
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == payload.plan_id,
        SubscriptionPlan.is_active == True
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    # Calculate amount based on billing cycle
    amount = plan.price_monthly if payload.billing_cycle == "monthly" else plan.price_yearly
    
    if not amount or amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid amount for {payload.billing_cycle} billing"
        )
    
    # Create payment order in gateway
    gateway_client = PaymentGatewayFactory.get_client()
    order = gateway_client.create_order(
        amount=amount,
        currency="INR",
        receipt=f"sub_{org.id}_{plan.id}",
        notes={
            "organization_id": org.id,
            "organization_name": org.name,
            "plan_id": plan.id,
            "plan_name": plan.name,
            "billing_cycle": payload.billing_cycle
        }
    )
    
    # Create payment record
    payment = Payment(
        organization_id=org.id,
        payment_method_id=payload.payment_method_id,
        amount=amount,
        currency="INR",
        payment_type="subscription",
        billing_cycle=payload.billing_cycle,
        payment_gateway=settings.PAYMENT_GATEWAY,
        gateway_order_id=order["id"],
        payment_status="pending",
        description=f"Subscription payment for {plan.name} plan ({payload.billing_cycle})",
        gateway_metadata=str(order)
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return PaymentInitiateResponse(
        order_id=str(payment.id),
        amount=amount,
        currency="INR",
        payment_gateway=settings.PAYMENT_GATEWAY,
        gateway_order_id=order["id"],
        gateway_key_id=settings.RAZORPAY_KEY_ID if settings.PAYMENT_GATEWAY == "razorpay" else None
    )


# ============================================
# VERIFY PAYMENT
# ============================================
@router.post("/verify", response_model=PaymentVerifyResponse)
async def verify_payment(
    payload: PaymentVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_admin)
):
    """
    Verify payment after completion
    Updates payment status and activates subscription
    """
    # Find payment record
    payment = db.query(Payment).filter(
        Payment.gateway_order_id == payload.gateway_order_id,
        Payment.organization_id == current_user.organization_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Verify payment signature
    gateway_client = PaymentGatewayFactory.get_client()
    is_valid = gateway_client.verify_payment_signature(
        payload.gateway_payment_id,
        payload.gateway_order_id,
        payload.gateway_signature
    )
    
    if not is_valid:
        payment.payment_status = "failed"
        payment.description = "Payment signature verification failed"
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment signature"
        )
    
    # Update payment record
    payment.payment_status = "completed"
    payment.gateway_payment_id = payload.gateway_payment_id
    payment.gateway_signature = payload.gateway_signature
    payment.payment_date = date.today()
    
    # Get organization and plan
    org = db.query(Organization).filter(
        Organization.id == payment.organization_id
    ).first()
    
    # Determine plan from payment description or metadata
    # For now, we'll get it from the organization's plan_id if set
    # In production, you'd parse from payment metadata
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == org.plan_id
    ).first()
    
    subscription_activated = False
    
    # Activate subscription if it's a subscription payment
    if payment.payment_type == "subscription" and plan:
        SubscriptionManager.activate_subscription(
            db, org, plan, payment.billing_cycle, payment
        )
        subscription_activated = True
    else:
        # Just update payment totals
        org.last_payment_date = date.today()
        org.total_amount_paid += payment.amount
        db.commit()
    
    return PaymentVerifyResponse(
        success=True,
        payment_id=payment.id,
        message="Payment verified successfully",
        subscription_activated=subscription_activated
    )


# ============================================
# GET PAYMENT HISTORY
# ============================================
@router.get("/history", response_model=PaymentHistoryResponse)
async def get_payment_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get payment history for organization
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization assigned"
        )
    
    payments = db.query(Payment).filter(
        Payment.organization_id == current_user.organization_id
    ).order_by(Payment.created_at.desc()).all()
    
    total_amount = sum(p.amount for p in payments if p.payment_status == "completed")
    
    return PaymentHistoryResponse(
        payments=payments,
        total_payments=len(payments),
        total_amount_paid=total_amount
    )


# ============================================
# GET PAYMENT DETAILS
# ============================================
@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment_details(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific payment details
    """
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.organization_id == current_user.organization_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


# ============================================
# WEBHOOK HANDLER
# ============================================
@router.post("/webhook")
async def handle_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle payment gateway webhooks
    Processes payment events from Razorpay/Stripe
    """
    # Get raw body and signature
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature") or request.headers.get("Stripe-Signature")
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing webhook signature"
        )
    
    # Verify webhook signature
    is_valid = WebhookHandler.verify_webhook_signature(
        body.decode("utf-8"),
        signature,
        settings.PAYMENT_GATEWAY
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    
    # Parse event data
    import json
    event_data = json.loads(body)
    event_type = event_data.get("event")
    
    # Process webhook
    success = WebhookHandler.process_webhook(
        db,
        event_type,
        event_data,
        settings.PAYMENT_GATEWAY
    )
    
    if success:
        return {"status": "success", "message": "Webhook processed"}
    else:
        return {"status": "error", "message": "Webhook processing failed"}
