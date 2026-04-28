from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database import get_db
from app.models.user_m import User
from app.models.organization_m import Organization
from app.models.subscription_plans_m import SubscriptionPlan
from app.models.payment_m import Payment
from app.dependencies import get_current_user, require_org_admin
from app.schema.subscription_schema import (
    SubscriptionStatusResponse,
    TrialStatusResponse,
    ConvertTrialRequest,
    SubscriptionUpgradeRequest,
    SubscriptionDowngradeRequest,
    SubscriptionCancelRequest,
    SubscriptionActionResponse
)
from app.utils.subscription_manager import SubscriptionManager
from app.utils.payment_gateway import PaymentGatewayFactory
from app.config import settings

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


# ============================================
# GET SUBSCRIPTION STATUS
# ============================================
@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current subscription status for user's organization
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization assigned to your account"
        )
    
    org = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Calculate trial days remaining
    trial_days_remaining = None
    if org.is_trial and org.trial_end_date:
        days = (org.trial_end_date - date.today()).days
        trial_days_remaining = max(0, days)
    
    return SubscriptionStatusResponse(
        organization_id=org.id,
        organization_name=org.name,
        plan_id=org.plan_id,
        plan_name=org.plan.name if org.plan else None,
        subscription_status=org.subscription_status,
        subscription_start_date=org.subscription_start_date,
        subscription_end_date=org.subscription_end_date,
        next_billing_date=org.next_billing_date,
        is_trial=org.is_trial,
        trial_start_date=org.trial_start_date,
        trial_end_date=org.trial_end_date,
        trial_days_remaining=trial_days_remaining,
        branch_limit=org.branch_limit,
        current_branches=org.current_branches,
        user_limit=org.user_limit,
        current_users=org.current_users,
        storage_limit_mb=org.storage_limit_mb,
        current_storage_mb=org.current_storage_mb,
        last_payment_date=org.last_payment_date,
        total_amount_paid=org.total_amount_paid
    )


# ============================================
# GET TRIAL STATUS
# ============================================
@router.get("/trial-status", response_model=TrialStatusResponse)
async def get_trial_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get trial period status
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization assigned"
        )
    
    org = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    trial_status = SubscriptionManager.check_trial_status(org)
    
    return TrialStatusResponse(**trial_status)


# ============================================
# CONVERT TRIAL TO PAID
# ============================================
@router.post("/convert-trial", response_model=SubscriptionActionResponse)
async def convert_trial_to_paid(
    payload: ConvertTrialRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_admin)
):
    """
    Convert trial subscription to paid subscription
    Requires payment
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization assigned"
        )
    
    org = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not org.is_trial:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization is not in trial period"
        )
    
    # Check if trial has expired
    trial_status = SubscriptionManager.check_trial_status(org)
    if not trial_status["can_convert_to_paid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trial has expired beyond grace period"
        )
    
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
    
    # Calculate amount
    amount = plan.price_monthly if payload.billing_cycle == "monthly" else plan.price_yearly
    
    # Create payment order
    gateway_client = PaymentGatewayFactory.get_client()
    order = gateway_client.create_order(
        amount=amount,
        currency="INR",
        receipt=f"trial_conversion_{org.id}",
        notes={
            "organization_id": org.id,
            "plan_id": plan.id,
            "billing_cycle": payload.billing_cycle
        }
    )
    
    # Create payment record
    payment = Payment(
        organization_id=org.id,
        amount=amount,
        currency="INR",
        payment_type="subscription",
        billing_cycle=payload.billing_cycle,
        payment_gateway=settings.PAYMENT_GATEWAY,
        gateway_order_id=order["id"],
        payment_status="pending",
        description=f"Trial conversion to {plan.name} plan"
    )
    
    db.add(payment)
    db.commit()
    
    return SubscriptionActionResponse(
        success=True,
        message="Payment order created. Complete payment to activate subscription.",
        payment_required=True,
        payment_order_id=order["id"]
    )


# ============================================
# UPGRADE SUBSCRIPTION
# ============================================
@router.post("/upgrade", response_model=SubscriptionActionResponse)
async def upgrade_subscription(
    payload: SubscriptionUpgradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_admin)
):
    """
    Upgrade to a higher subscription plan
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization assigned"
        )
    
    org = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if org.is_trial:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please convert trial to paid subscription first"
        )
    
    # Get current and new plans
    current_plan = org.plan
    new_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == payload.new_plan_id,
        SubscriptionPlan.is_active == True
    ).first()
    
    if not new_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    if new_plan.price_monthly <= current_plan.price_monthly:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New plan must be higher tier than current plan. Use downgrade endpoint instead."
        )
    
    # Calculate prorated amount
    org_updated, prorated_amount = SubscriptionManager.upgrade_subscription(
        db, org, new_plan, current_plan
    )
    
    if prorated_amount > 0:
        # Create payment order for prorated amount
        gateway_client = PaymentGatewayFactory.get_client()
        order = gateway_client.create_order(
            amount=prorated_amount,
            currency="INR",
            receipt=f"upgrade_{org.id}",
            notes={
                "organization_id": org.id,
                "from_plan_id": current_plan.id,
                "to_plan_id": new_plan.id
            }
        )
        
        # Create payment record
        payment = Payment(
            organization_id=org.id,
            amount=prorated_amount,
            currency="INR",
            payment_type="subscription_upgrade",
            payment_gateway=settings.PAYMENT_GATEWAY,
            gateway_order_id=order["id"],
            payment_status="pending",
            description=f"Upgrade from {current_plan.name} to {new_plan.name}"
        )
        
        db.add(payment)
        db.commit()
        
        return SubscriptionActionResponse(
            success=True,
            message=f"Upgrade initiated. Prorated amount: ₹{prorated_amount}",
            payment_required=True,
            payment_order_id=order["id"]
        )
    else:
        return SubscriptionActionResponse(
            success=True,
            message=f"Successfully upgraded to {new_plan.name}",
            payment_required=False
        )


# ============================================
# DOWNGRADE SUBSCRIPTION
# ============================================
@router.post("/downgrade", response_model=SubscriptionActionResponse)
async def downgrade_subscription(
    payload: SubscriptionDowngradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_admin)
):
    """
    Downgrade to a lower subscription plan
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization assigned"
        )
    
    org = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    # Get new plan
    new_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == payload.new_plan_id,
        SubscriptionPlan.is_active == True
    ).first()
    
    if not new_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    # Downgrade
    effective_immediately = payload.effective_date is None or payload.effective_date <= date.today()
    org_updated = SubscriptionManager.downgrade_subscription(
        db, org, new_plan, effective_immediately
    )
    
    return SubscriptionActionResponse(
        success=True,
        message=f"Successfully downgraded to {new_plan.name}",
        payment_required=False
    )


# ============================================
# CANCEL SUBSCRIPTION
# ============================================
@router.post("/cancel", response_model=SubscriptionActionResponse)
async def cancel_subscription(
    payload: SubscriptionCancelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_admin)
):
    """
    Cancel subscription
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization assigned"
        )
    
    org = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    org_updated = SubscriptionManager.cancel_subscription(
        db, org, payload.cancel_immediately
    )
    
    message = "Subscription cancelled immediately" if payload.cancel_immediately else \
              "Subscription will be cancelled at end of billing period"
    
    return SubscriptionActionResponse(
        success=True,
        message=message,
        payment_required=False
    )
