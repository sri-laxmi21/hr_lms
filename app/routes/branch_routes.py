from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission,
)

from app.models.branch_m import Branch
from app.models.organization_m import Organization
from app.models.subscription_plans_m import SubscriptionPlan
from app.schema.branch_schema import BranchCreate, BranchResponse, BranchUpdate


router = APIRouter(prefix="/branches", tags=["branches"])

# ✅ Menu ID from your seeder
BRANCHES_MENU_ID = 8


# -------------------------------------------------
# CREATE BRANCH (PLAN-BASED LIMIT ENFORCED)
# -------------------------------------------------
@router.post(
    "/",
    response_model=BranchResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_create_permission(BRANCHES_MENU_ID))]
)
def create_branch(
    payload: BranchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 1️⃣ Validate user org
    org_id = current_user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="User not assigned to any organization")

    organization = db.query(Organization).filter(
        Organization.id == org_id,
        Organization.is_active == True
    ).first()

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    # 2️⃣ Validate subscription status
    if organization.subscription_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription is not active"
        )

    # 3️⃣ Fetch subscription plan
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == organization.plan_id,
        SubscriptionPlan.is_active == True
    ).first()

    if not plan:
        raise HTTPException(
            status_code=400,
            detail="No active subscription plan assigned"
        )

    # 4️⃣ Count existing branches
    current_branches = db.query(Branch).filter(
        Branch.organization_id == org_id
    ).count()

    # 5️⃣ Enforce plan branch limit
    if current_branches >= plan.branch_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Branch limit reached for {plan.name} plan"
        )

    # 6️⃣ Prevent duplicate branch names per org
    existing = db.query(Branch).filter(
        Branch.name == payload.name,
        Branch.organization_id == org_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Branch with this name already exists in your organization"
        )

    # 7️⃣ Create branch
    new_branch = Branch(
        **payload.dict(),
        organization_id=org_id
    )

    db.add(new_branch)

    # 8️⃣ Update usage tracking
    organization.current_branches = current_branches + 1

    db.commit()
    db.refresh(new_branch)

    return new_branch


# -------------------------------------------------
# LIST BRANCHES (ORG-SCOPED)
# -------------------------------------------------
@router.get(
    "/",
    response_model=List[BranchResponse],
    dependencies=[Depends(require_view_permission(BRANCHES_MENU_ID))]
)
def list_branches(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Branch).filter(
        Branch.organization_id == current_user.organization_id
    ).all()


# -------------------------------------------------
# GET BRANCH BY ID (ORG SAFE)
# -------------------------------------------------
@router.get(
    "/{branch_id}",
    response_model=BranchResponse,
    dependencies=[Depends(require_view_permission(BRANCHES_MENU_ID))]
)
def get_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    branch = db.query(Branch).filter(
        Branch.id == branch_id,
        Branch.organization_id == current_user.organization_id
    ).first()

    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    return branch


# -------------------------------------------------
# UPDATE BRANCH
# -------------------------------------------------
@router.put(
    "/{branch_id}",
    response_model=BranchResponse,
    dependencies=[Depends(require_edit_permission(BRANCHES_MENU_ID))]
)
def update_branch(
    branch_id: int,
    payload: BranchUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    branch = db.query(Branch).filter(
        Branch.id == branch_id,
        Branch.organization_id == current_user.organization_id
    ).first()

    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(branch, key, value)

    db.commit()
    db.refresh(branch)

    return branch


# -------------------------------------------------
# DELETE BRANCH (USAGE UPDATED)
# -------------------------------------------------
@router.delete(
    "/{branch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_delete_permission(BRANCHES_MENU_ID))]
)
def delete_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()

    branch = db.query(Branch).filter(
        Branch.id == branch_id,
        Branch.organization_id == current_user.organization_id
    ).first()

    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    db.delete(branch)

    # Safe decrement
    if organization and organization.current_branches > 0:
        organization.current_branches -= 1

    db.commit()
