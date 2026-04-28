from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from typing import Optional, List
from app.models.payment_m import Payment
from app.database import get_db
from app.models.organization_m import Organization
from app.models.subscription_plans_m import SubscriptionPlan
from app.models.user_m import User
from app.dependencies import require_super_admin
from datetime import datetime
from sqlalchemy import func, case

router = APIRouter(
    prefix="/super-admin",
    tags=["Super Admin – Dashboard & Client Management"]
)

# ----------------------------------------
# SUPER ADMIN DASHBOARD ROUTES
# ----------------------------------------
@router.get("/dashboard/stats")
def super_admin_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    📊 Product-level dashboard metrics
    """

    total_orgs = db.query(Organization).count()

    active_orgs = db.query(Organization).filter(
        Organization.subscription_status == "active"
    ).count()

    trial_orgs = db.query(Organization).filter(
        Organization.subscription_status == "trial"
    ).count()

    expired_orgs = db.query(Organization).filter(
        Organization.subscription_status == "expired"
    ).count()

    total_users = db.query(User).count()

    return {
        "organizations": {
            "total": total_orgs,
            "active": active_orgs,
            "trial": trial_orgs,
            "expired": expired_orgs
        },
        "users": {
            "total": total_users
        },
        "revenue": {
            "monthly": None  # Optional: integrate payments later
        }
    }

# ----------------------------------------
# CLIENT ORGANIZATION MANAGEMENT
# ----------------------------------------


@router.get("/clients")
def get_all_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    🏢 Get all client organizations (Super Admin)
    """

    orgs = db.query(Organization).order_by(Organization.created_at.desc()).all()

    return [
        {
            "id": org.id,
            "name": org.name,
            "description": org.description,
            "contact_email": org.contact_email,
            "contact_phone": org.contact_phone,
            "subscription_status": org.subscription_status,
            "plan": org.plan.name if org.plan else None,
            "limits": {
                "users": org.user_limit,
                "branches": org.branch_limit,
                "storage_mb": org.storage_limit_mb
            },
            "usage": {
                "current_users": org.current_users,
                "current_branches": org.current_branches
            },
            "subscription_end_date": org.subscription_end_date,
            "created_at": org.created_at
        }
        for org in orgs
    ]

# ----------------------------------------
# CLIENT ORGANIZATION SUBSCRIPTION MANAGEMENT
# ----------------------------------------

@router.patch("/clients/{org_id}/status")
def update_client_status(
    org_id: int,
    status_value: str,
    extend_trial_days: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    🔄 Update client subscription status
    """

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")

    allowed_status = ["active", "trial", "suspended", "expired"]
    if status_value not in allowed_status:
        raise HTTPException(400, "Invalid subscription status")

    org.subscription_status = status_value

    # Extend trial if requested
    if status_value == "trial" and extend_trial_days:
        org.subscription_end_date = date.today() + timedelta(days=extend_trial_days)

    # Suspend org (blocks login via middleware)
    if status_value == "suspended":
        org.is_active = False
    else:
        org.is_active = True

    db.commit()

    return {
        "message": "Organization subscription status updated",
        "organization_id": org.id,
        "status": org.subscription_status,
        "subscription_end_date": org.subscription_end_date
    }
# ----------------------------------------
# ASSIGN/CHANGE SUBSCRIPTION PLAN FOR CLIENT
# ----------------------------------------  

@router.patch("/clients/{org_id}/plan")
def assign_or_change_plan(
    org_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    📦 Assign or change subscription plan for an organization
    """

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Organization not found")

    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == plan_id,
        SubscriptionPlan.is_active == True
    ).first()

    if not plan:
        raise HTTPException(404, "Subscription plan not found or inactive")

    # Assign plan & sync limits
    org.plan_id = plan.id
    org.branch_limit = plan.branch_limit
    org.user_limit = plan.user_limit
    org.storage_limit_mb = plan.storage_limit_mb
    org.subscription_status = "active"
    org.subscription_end_date = None

    db.commit()

    return {
        "message": "Subscription plan assigned successfully",
        "organization_id": org.id,
        "plan": plan.name
    }
# ----------------------------------------
# GET DETAILED ORGANIZATION PROFILE
# ----------------------------------------
@router.get("/clients/{org_id}")
def get_client_details(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    🏢 Get detailed organization profile (Super Admin)
    """

    org = db.query(Organization).filter(
        Organization.id == org_id
    ).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return {
        "id": org.id,
        "name": org.name,
        "description": org.description,
        "contact_email": org.contact_email,
        "contact_phone": org.contact_phone,
        "subscription_status": org.subscription_status,
        "plan": org.plan.name if org.plan else None,
        "limits": {
            "users": org.user_limit,
            "branches": org.branch_limit,
            "storage_mb": org.storage_limit_mb
        },
        "usage": {
            "current_users": org.current_users,
            "current_branches": org.current_branches
        },
        "subscription_end_date": (
            org.subscription_end_date.isoformat()
            if org.subscription_end_date else None
        ),
        "created_at": org.created_at.isoformat()
    }
# ----------------------------------------
# SOFT DELETE EXPIRED TRIAL ORGANIZATION
# ----------------------------------------

@router.delete("/clients/{org_id}")
def soft_delete_expired_trial(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    ❌ Soft delete an organization
    Only allowed if the organization is on trial and the trial has expired.
    """

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check trial status and if subscription has expired
    if org.subscription_status != "trial":
        raise HTTPException(
            status_code=400,
            detail="Only trial organizations can be deleted"
        )

    if org.subscription_end_date and org.subscription_end_date > date.today():
        raise HTTPException(
            status_code=400,
            detail="Trial period has not ended yet"
        )

    # Soft delete
    org.is_active = False
    db.commit()

    return {
        "message": "Organization soft-deleted successfully",
        "organization_id": org.id,
        "name": org.name,
        "subscription_status": org.subscription_status
    }
# ----------------------------------------
# REVENUE REPORTING ROUTES
# ----------------------------------------

@router.get("/summary/plan/{plan_id}")
def get_plan_revenue_summary(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    💰 Revenue summary for a single subscription plan
    """

    # Validate plan
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == plan_id
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")

    # Active organizations on this plan
    active_orgs = db.query(Organization).filter(
        Organization.plan_id == plan_id,
        Organization.subscription_status == "active"
    ).count()

    # Revenue aggregation
    revenue_data = db.query(
        func.count(Payment.id).label("subscriptions_sold"),
        func.sum(
            case(
                (Payment.billing_cycle == "monthly", Payment.amount),
                else_=0
            )
        ).label("monthly_revenue"),
        func.sum(
            case(
                (Payment.billing_cycle == "yearly", Payment.amount),
                else_=0
            )
        ).label("yearly_revenue"),
        func.sum(Payment.amount).label("total_revenue")
    ).filter(
        Payment.plan_id == plan_id,
        Payment.status == "completed",
        Payment.payment_type == "subscription"
    ).first()

    return {
        "success": True,
        "data": {
            "currency": "INR",
            "plan": {
                "plan_id": plan.id,
                "plan_name": plan.name,
                "active_organizations": active_orgs,
                "subscriptions_sold": revenue_data.subscriptions_sold or 0,
                "monthly_revenue": int(revenue_data.monthly_revenue or 0),
                "yearly_revenue": int(revenue_data.yearly_revenue or 0),
                "total_revenue": int(revenue_data.total_revenue or 0)
            },
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
    }
# ----------------------------------------
# REVENUE SUMMARY FOR ALL PLANS
# ----------------------------------------

@router.get("/summary")
def get_all_plans_revenue_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    💰 Revenue summary for ALL subscription plans
    """

    plans = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.is_active == True
    ).all()

    plans_data = []
    total_revenue = 0

    for plan in plans:
        active_orgs = db.query(Organization).filter(
            Organization.plan_id == plan.id,
            Organization.subscription_status == "active"
        ).count()

        revenue = db.query(
            func.count(Payment.id).label("subscriptions_sold"),
            func.sum(
                case(
                    (Payment.billing_cycle == "monthly", Payment.amount),
                    else_=0
                )
            ).label("monthly_revenue"),
            func.sum(
                case(
                    (Payment.billing_cycle == "yearly", Payment.amount),
                    else_=0
                )
            ).label("yearly_revenue"),
            func.sum(Payment.amount).label("total_revenue")
        ).filter(
            Payment.plan_id == plan.id,
            Payment.status == "completed",
            Payment.payment_type == "subscription"
        ).first()

        plan_total = int(revenue.total_revenue or 0)
        total_revenue += plan_total

        plans_data.append({
            "plan_id": plan.id,
            "plan_name": plan.name,
            "active_organizations": active_orgs,
            "subscriptions_sold": revenue.subscriptions_sold or 0,
            "monthly_revenue": int(revenue.monthly_revenue or 0),
            "yearly_revenue": int(revenue.yearly_revenue or 0),
            "total_revenue": plan_total
        })

    return {
        "success": True,
        "data": {
            "currency": "INR",
            "total_revenue": total_revenue,
            "plans": plans_data,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
    }