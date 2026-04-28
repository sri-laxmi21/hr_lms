from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.subscription_plans_m import SubscriptionPlan
from app.models.organization_m import Organization
from app.models.subscription_plan_module_m import SubscriptionPlanModule
from app.models.module_m import Module
from app.schema.module_schema import ModuleOut
from app.schema.subscription_plans_schema import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanResponse,
    SubscriptionPlanPublicResponse,
    PlanComparisonResponse
)
from app.dependencies import (
    require_super_admin,
    get_current_user,
    get_current_user_optional
)
from app.models.user_m import User

router = APIRouter(prefix="/subscription-plans", tags=["Subscription Plans"])


# ============================================
# CREATE PLAN (Super Admin Only)
# ============================================
@router.post("/", response_model=SubscriptionPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription_plan(
    payload: SubscriptionPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    ✅ Create new subscription plan
    - Only super admin can create plans
    - Plan names must be unique
    """
    
    # Check if plan name already exists
    existing = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.name == payload.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subscription plan '{payload.name}' already exists"
        )
    
    new_plan = SubscriptionPlan(
        **payload.dict(),
        created_by=f"{current_user.first_name} {current_user.last_name}",
        modified_by=f"{current_user.first_name} {current_user.last_name}"
    )
    
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    
    return new_plan


# ============================================
# GET ALL PLANS (Admin View)
# ============================================
@router.get("/admin/all", response_model=List[SubscriptionPlanResponse])
async def get_all_plans_admin(
    show_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    ✅ Get all subscription plans (admin view)
    - Only super admin can access
    - Can see inactive plans
    """
    
    query = db.query(SubscriptionPlan)
    
    if not show_inactive:
        query = query.filter(SubscriptionPlan.is_active == True)
    
    plans = query.order_by(SubscriptionPlan.display_order).all()

    for plan in plans:
        plan.modules = [pm.module for pm in plan.plan_modules]
    return plans


# ============================================
# GET PUBLIC PLANS (For Pricing Page)
# ============================================
@router.get("/public", response_model=List[SubscriptionPlanPublicResponse])
async def get_public_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    ✅ Get active subscription plans for pricing page
    - Public endpoint (no auth required)
    - Only shows active plans
    - Shows calculated savings
    """
    
    plans = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.is_active == True
    ).order_by(SubscriptionPlan.display_order).all()
    
    # Attach modules to each plan
    for plan in plans:
        plan.modules = [pm.module for pm in plan.plan_modules]
    
    return plans


# ============================================
# GET PLAN COMPARISON
# ============================================
@router.get("/compare", response_model=List[PlanComparisonResponse])
async def compare_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    ✅ Get plan comparison for frontend
    - Shows all active plans with features
    - Highlights current user's plan if logged in
    """
    
    plans = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.is_active == True
    ).order_by(SubscriptionPlan.display_order).all()
    
    current_plan_id = None
    if current_user and current_user.organization:
        current_plan_id = current_user.organization.plan_id
    
    comparison = []
    for plan in plans:
        comparison.append(
            PlanComparisonResponse(
                plan_id=plan.id,
                plan_name=plan.name,
                price_monthly=plan.price_monthly,
                features={
                    "branches": plan.branch_limit,
                    "users": plan.user_limit,
                    "storage_gb": round(plan.storage_limit_mb / 1024, 2),
                    "analytics": plan.has_analytics,
                    "api_access": plan.has_api_access,
                    "priority_support": plan.has_priority_support,
                    "whatsapp_notifications": plan.has_whatsapp_notifications,
                    "custom_branding": plan.has_custom_branding
                },
                is_current_plan=(plan.id == current_plan_id),
                is_recommended=(plan.name == "Standard")  # Mark Standard as recommended
            )
        )
    
    return comparison


# ============================================
# GET MY ORGANIZATION'S PLAN
# ============================================
@router.get("/my-plan", response_model=SubscriptionPlanResponse)
async def get_my_organization_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✅ Get current user's organization subscription plan
    - Returns plan details with usage limits
    """
    
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization assigned to your account"
        )
    
    org = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not org or not org.plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription plan assigned to your organization"
        )
    
    return org.plan


# ============================================
# GET SINGLE PLAN BY ID
# ============================================
@router.get("/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_plan_by_id(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    ✅ Get specific plan details
    - Public endpoint
    """
    
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == plan_id,
        SubscriptionPlan.is_active == True
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    return plan


# ============================================
# UPDATE PLAN (Super Admin Only)
# ============================================
@router.put("/{plan_id}", response_model=SubscriptionPlanResponse)
async def update_subscription_plan(
    plan_id: int,
    payload: SubscriptionPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    ✅ Update subscription plan
    - Only super admin can update
    - Updates all organizations using this plan
    """
    
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == plan_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    # Check if name is being changed and if it conflicts
    if payload.name and payload.name != plan.name:
        existing = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == payload.name,
            SubscriptionPlan.id != plan_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plan name '{payload.name}' already exists"
            )
    
    # Update plan fields
    update_data = payload.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(plan, key, value)
    
    plan.modified_by = f"{current_user.first_name} {current_user.last_name}"
    
    db.commit()
    db.refresh(plan)
    
    # 🔥 Update all organizations using this plan
    if any(key in update_data for key in ["branch_limit", "user_limit", "storage_limit_mb"]):
        organizations = db.query(Organization).filter(
            Organization.plan_id == plan_id
        ).all()
        
        for org in organizations:
            if "branch_limit" in update_data:
                org.branch_limit = plan.branch_limit
            if "user_limit" in update_data:
                org.user_limit = plan.user_limit
            if "storage_limit_mb" in update_data:
                org.storage_limit_mb = plan.storage_limit_mb
        
        db.commit()
    
    return plan


# ============================================
# DELETE PLAN (Super Admin Only)
# ============================================
@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    ✅ Delete subscription plan
    - Only super admin can delete
    - Cannot delete if organizations are using it
    """
    
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == plan_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    # Check if any organizations are using this plan
    orgs_count = db.query(Organization).filter(
        Organization.plan_id == plan_id
    ).count()
    
    if orgs_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete plan. {orgs_count} organization(s) are currently using it. "
                   f"Please migrate them to another plan first."
        )
    
    db.delete(plan)
    db.commit()
    
    return None


# ============================================
# DEACTIVATE PLAN (Soft Delete)
# ============================================
@router.patch("/{plan_id}/deactivate")
async def deactivate_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    ✅ Deactivate subscription plan (soft delete)
    - Only super admin can deactivate
    - Existing organizations keep the plan
    - New organizations cannot select it
    """
    
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == plan_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    plan.is_active = False
    plan.modified_by = f"{current_user.first_name} {current_user.last_name}"
    
    db.commit()
    db.refresh(plan)
    
    return {
        "message": f"Plan '{plan.name}' has been deactivated",
        "organizations_affected": db.query(Organization).filter(
            Organization.plan_id == plan_id
        ).count()
    }


# ============================================
# REACTIVATE PLAN
# ============================================
@router.patch("/{plan_id}/activate")
async def activate_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    ✅ Reactivate subscription plan
    - Only super admin can reactivate
    """
    
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == plan_id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    plan.is_active = True
    plan.modified_by = f"{current_user.first_name} {current_user.last_name}"
    
    db.commit()
    db.refresh(plan)
    
    return {
        "message": f"Plan '{plan.name}' has been reactivated"
    }