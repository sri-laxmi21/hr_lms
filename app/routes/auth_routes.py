from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database import get_db
from app.models.user_m import User
from app.models.role_m import Role
from app.models.organization_m import Organization
from app.models.subscription_plans_m import SubscriptionPlan
from app.models.menu_m import Menu
from app.models.role_right_m import RoleRight
from app.schema.user_schema import AuthRegister, AuthRegisterResponse
from app.utils.utils import hash_password, verify_password, create_access_token
from app.middleware.tenant_limits import TenantLimitsMiddleware
from app.dependencies import get_current_user
from app.config import settings

from app.database import get_db
from app.models.user_m import User
from app.models.role_m import Role
from app.models.organization_m import Organization
from app.models.subscription_plans_m import SubscriptionPlan
from app.models.menu_m import Menu
from app.models.role_right_m import RoleRight
from app.schema.user_schema import AuthRegister, AuthRegisterResponse
from app.utils.utils import hash_password, verify_password, create_access_token
from app.middleware.tenant_limits import TenantLimitsMiddleware
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


# ============================================
# HELPER: Get User Menus Based on Role Rights
# ============================================
def get_user_accessible_menus(user: User, db: Session):
    """
    ✅ Get menus accessible by user
    - super_admin: ALL menus (platform-wide)
    - org_admin or is_org_admin=True: ALL menus (organization-wide)
    - manager/employee: menus based on role rights
    """
    
    # 🔥 Check if user is super_admin or org_admin
    is_super_admin = user.role and user.role.name.lower() == "super_admin"
    is_org_admin_role = user.role and user.role.name.lower() == "org_admin"
    
    # Organization admin gets full access
    if user.is_org_admin or is_org_admin_role or is_super_admin:
        accessible_menus = (
            db.query(Menu)
            .filter(Menu.is_active == True)
            .order_by(Menu.menu_order)
            .all()
        )
    else:
        # Regular user (employee/manager) - check role rights
        accessible_menu_ids = (
            db.query(RoleRight.menu_id)
            .filter(
                RoleRight.role_id == user.role_id,
                RoleRight.can_view == True
            )
            .all()
        )
        
        menu_ids = [menu_id[0] for menu_id in accessible_menu_ids]
        
        if not menu_ids:
            return []
        
        accessible_menus = (
            db.query(Menu)
            .filter(
                Menu.id.in_(menu_ids),
                Menu.is_active == True
            )
            .order_by(Menu.menu_order)
            .all()
        )
    
    # Build menu tree
    menu_dict = {}
    for menu in accessible_menus:
        menu_dict[menu.id] = {
            "id": menu.id,
            "name": menu.name,
            "display_name": menu.display_name,
            "route": menu.route,
            "icon": menu.icon,
            "parent_id": menu.parent_id,
            "menu_order": menu.menu_order,
            "children": []
        }
    
    # Build parent-child relationships
    root_menus = []
    for menu_id, menu_data in menu_dict.items():
        if menu_data["parent_id"] is None:
            root_menus.append(menu_data)
        else:
            # Find parent and add as child
            parent = menu_dict.get(menu_data["parent_id"])
            if parent:
                parent["children"].append(menu_data)
    
    return root_menus


def get_user_menu_permissions(user: User, db: Session):
    """
    ✅ Get all menu permissions for user
    - super_admin/org_admin: full permissions on ALL menus
    - manager/employee: permissions based on role rights
    """
    
    # 🔥 Check if user is super_admin or org_admin
    is_super_admin = user.role and user.role.name.lower() == "super_admin"
    is_org_admin_role = user.role and user.role.name.lower() == "org_admin"
    
    if user.is_org_admin or is_org_admin_role or is_super_admin:
        # Get all active menus and grant full permissions
        all_menus = db.query(Menu).filter(Menu.is_active == True).all()
        
        permissions = {}
        for menu in all_menus:
            permissions[menu.id] = {
                "can_view": True,
                "can_create": True,
                "can_edit": True,
                "can_delete": True
            }
        
        return permissions
    
    # Regular user - get permissions from role rights
    role_rights = (
        db.query(RoleRight)
        .filter(RoleRight.role_id == user.role_id)
        .all()
    )
    
    permissions = {}
    for rr in role_rights:
        permissions[rr.menu_id] = {
            "can_view": rr.can_view,
            "can_create": rr.can_create,
            "can_edit": rr.can_edit,
            "can_delete": rr.can_delete
        }
    
    return permissions


# ============================================
# REGISTER (Auto-creates Organization)
# ============================================
@router.post("/register", response_model=AuthRegisterResponse)
async def register(user: AuthRegister, db: Session = Depends(get_db)):
    """
    ✅ User registration with automatic organization creation
    - Creates new organization for the user
    - Assigns default "Basic" plan with 30-day trial
    - Makes first user the organization admin with "org_admin" role
    - Auto-initializes limits from plan
    """
    
    # Check if email already exists (globally)
    existing_user = db.query(User).filter(User.email == user.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 🔥 Get or create default "Basic" plan
    default_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.name == "Basic",
        SubscriptionPlan.is_active == True
    ).first()
    
    if not default_plan:
        # If no plan exists, create a default one
        default_plan = SubscriptionPlan(
            name="Basic",
            description="Free trial plan with basic features",
            price_monthly=0,
            branch_limit=2,
            user_limit=10,
            storage_limit_mb=1000,
            has_analytics=False,
            has_api_access=False,
            has_priority_support=False,
            has_whatsapp_notifications=False,
            has_custom_branding=False,
            is_active=True,
            display_order=1
        )
        db.add(default_plan)
        db.flush()
    
    # 🔥 Create Organization automatically
    organization_name = user.organization_name or f"{user.first_name}'s Organization"
    
    # Check if organization name already exists
    existing_org = db.query(Organization).filter(
        Organization.name == organization_name
    ).first()
    
    if existing_org:
        # Add unique suffix if name exists
        counter = 1
        while existing_org:
            organization_name = f"{user.organization_name or user.first_name}'s Organization {counter}"
            existing_org = db.query(Organization).filter(
                Organization.name == organization_name
            ).first()
            counter += 1
    
    trial_days = settings.TRIAL_PERIOD_DAYS
    trial_end = date.today() + timedelta(days=trial_days)
    
    new_org = Organization(
        name=organization_name,
        description=f"Organization for {user.first_name} {user.last_name or ''}",
        plan_id=default_plan.id,
        
        # Subscription settings (trial period)
        subscription_status="trial",
        subscription_start_date=date.today(),
        subscription_end_date=trial_end,
        
        # Trial Period Fields
        is_trial=True,
        trial_start_date=date.today(),
        trial_end_date=trial_end,
        trial_days=trial_days,
        
        # Set limits from plan
        branch_limit=default_plan.branch_limit,
        user_limit=default_plan.user_limit,
        storage_limit_mb=default_plan.storage_limit_mb,
        
        # Initialize counters
        current_branches=0,
        current_users=1,  # This user
        current_storage_mb=0,
        
        # Billing info
        last_payment_date=None,
        next_billing_date=trial_end,
        total_amount_paid=0,
        
        # Contact info
        contact_email=user.email.lower(),
        contact_phone=user.contact_phone,
        
        is_active=True,
        created_by="System"
    )
    
    db.add(new_org)
    db.flush()  # Get org.id before creating user
    
    # 🔥 Assign "org_admin" role to first user (check by name)
    org_admin_role = db.query(Role).filter(
        Role.name == "org_admin"
    ).first()
    
    if not org_admin_role:
        # If org_admin role doesn't exist, create it
        org_admin_role = Role(name="org_admin")
        db.add(org_admin_role)
        db.flush()
    
    # 🔥 Create user and link to organization
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email.lower(),
        hashed_password=hash_password(user.password),
        role_id=org_admin_role.id,  # Assign org_admin role
        organization_id=new_org.id,
        branch_id=None,  # No branch initially
        is_org_admin=True,  # First user = organization admin
        inactive=False,
        created_by="System"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.refresh(new_org)
    
    # Calculate trial days remaining
    trial_days = (new_org.subscription_end_date - date.today()).days if new_org.subscription_end_date else 30
    
    # 🎉 Optional: Send welcome email
    # send_welcome_email(new_user.email, new_org.name, trial_days)
    
    return AuthRegisterResponse(
        user_id=new_user.id,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        email=new_user.email,
        organization_id=new_org.id,
        organization_name=new_org.name,
        is_org_admin=True,
        subscription_status=new_org.subscription_status,
        subscription_end_date=new_org.subscription_end_date,
        trial_days_remaining=trial_days
    )


# ============================================
# LOGIN (with menus and full profile)
# ============================================
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    ✅ User login with organization validation + menus
    - super_admin: ALL menus + full permissions (platform-wide)
    - org_admin or is_org_admin=True: ALL menus + full permissions (org-wide)
    - manager/employee: filtered menus + limited permissions
    - Returns user + organization + menus + permissions
    """
    
    # Find user by email
    user = db.query(User).filter(
        User.email == form_data.username.lower()
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # ❌ Check if user account is inactive
    if user.inactive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact your organization admin."
        )
    
    # 🔒 Check organization status (if user belongs to one)
    organization_status = None
    days_until_expiry = None
    org_data = None
    
    if user.organization_id:
        try:
            org = await TenantLimitsMiddleware.check_organization_status(
                organization_id=user.organization_id,
                db=db
            )
            organization_status = org.subscription_status
            
            # Calculate days until expiry
            if org.subscription_end_date:
                days_until_expiry = (org.subscription_end_date - date.today()).days
            
            # Organization data
            org_data = {
                "id": org.id,
                "name": org.name,
                "subscription_status": org.subscription_status,
                "subscription_end_date": str(org.subscription_end_date) if org.subscription_end_date else None,
                "is_active": org.is_active,
                "plan_name": org.plan.name if org.plan else None,
                "days_until_expiry": days_until_expiry,
                
                # Usage info
                "usage": {
                    "branches": {
                        "current": org.current_branches,
                        "limit": org.branch_limit,
                        "remaining": org.branch_limit - org.current_branches
                    },
                    "users": {
                        "current": org.current_users,
                        "limit": org.user_limit,
                        "remaining": org.user_limit - org.current_users
                    },
                    "storage_mb": {
                        "current": org.current_storage_mb,
                        "limit": org.storage_limit_mb,
                        "remaining": org.storage_limit_mb - org.current_storage_mb
                    }
                }
            }
                
        except HTTPException as e:
            # Organization subscription expired or suspended
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Organization access restricted: {e.detail}"
            )
    
    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # 🔥 Get user menus (org_admin/super_admin gets ALL menus)
    menus = get_user_accessible_menus(user, db)
    
    # 🔥 Get user permissions (org_admin/super_admin gets FULL permissions)
    permissions = get_user_menu_permissions(user, db)
    
    # Fetch role details
    role_name = user.role.name if user.role else None
    role_id = user.role.id if user.role else None
    
    # Fetch organization details
    org_name = user.organization.name if user.organization else None
    org_id = user.organization_id
    
    # Fetch branch details
    branch_name = user.branch.name if user.branch else None
    branch_id = user.branch_id
    
    # Fetch department details
    department_name = user.department.name if user.department else None
    department_id = user.department_id if hasattr(user, 'department_id') else None
    
    # 🔥 Determine access level based on role name
    is_super_admin = role_name and role_name.lower() == "super_admin"
    is_org_admin_role = role_name and role_name.lower() == "org_admin"
    has_full_access = user.is_org_admin or is_org_admin_role or is_super_admin
    
    # ✅ Return comprehensive response with menus
    return {
        "access_token": access_token,
        "token_type": "bearer",
        
        # 🔥 User Profile
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": f"{user.first_name} {user.last_name or ''}".strip(),
            "email": user.email,
            
            # Role info
            "role_id": role_id,
            "role_name": role_name,
            
            # Organization info
            "organization_id": org_id,
            "organization_name": org_name,
            "is_org_admin": user.is_org_admin,
            
            # Branch info
            "branch_id": branch_id,
            "branch_name": branch_name,
            
            # Department info
            "department_id": department_id,
            "department_name": department_name,
            
            # Additional info
            "designation": user.designation,
            "joining_date": str(user.joining_date) if user.joining_date else None,
            "inactive": user.inactive,
            "biometric_id": user.biometric_id
        },
        
        # 🔥 Organization Details
        "organization": org_data,
        
        # 🔥 User Menus (ALL for org_admin, filtered for regular users)
        "menus": menus,
        
        # 🔥 Menu Permissions (FULL for org_admin, limited for regular users)
        "permissions": permissions,
        
        # 🔥 Access level indicator
        "access_level": "full" if has_full_access else "limited"
    }


# ============================================
# GET AUTH STATUS WITH MENUS
# ============================================
@router.get("/me")
async def get_auth_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✅ Get current authentication status with menus
    - super_admin/org_admin get ALL menus with full permissions
    - Returns user info + organization status + menus
    - Useful for frontend to check session validity and load navigation
    """
    
    # Check organization status
    org_data = None
    days_until_expiry = None
    
    if current_user.organization_id:
        org = db.query(Organization).filter(
            Organization.id == current_user.organization_id
        ).first()
        
        if org:
            if org.subscription_end_date:
                days_until_expiry = (org.subscription_end_date - date.today()).days
            
            org_data = {
                "id": org.id,
                "name": org.name,
                "subscription_status": org.subscription_status,
                "subscription_end_date": str(org.subscription_end_date) if org.subscription_end_date else None,
                "is_active": org.is_active,
                "plan_name": org.plan.name if org.plan else None,
                "days_until_expiry": days_until_expiry,
                
                # Usage info
                "usage": {
                    "branches": {
                        "current": org.current_branches,
                        "limit": org.branch_limit
                    },
                    "users": {
                        "current": org.current_users,
                        "limit": org.user_limit
                    },
                    "storage_mb": {
                        "current": org.current_storage_mb,
                        "limit": org.storage_limit_mb
                    }
                }
            }
    
    # 🔥 Get user menus (org_admin gets ALL)
    menus = get_user_accessible_menus(current_user, db)
    
    # 🔥 Get user permissions (org_admin gets FULL)
    permissions = get_user_menu_permissions(current_user, db)
    
    # 🔥 Determine access level based on role name
    role_name = current_user.role.name if current_user.role else None
    is_super_admin = role_name and role_name.lower() == "super_admin"
    is_org_admin_role = role_name and role_name.lower() == "org_admin"
    has_full_access = current_user.is_org_admin or is_org_admin_role or is_super_admin
    
    return {
        "authenticated": True,
        
        # User profile
        "user": {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "full_name": f"{current_user.first_name} {current_user.last_name or ''}".strip(),
            "email": current_user.email,
            "role_id": current_user.role_id,
            "role_name": role_name,
            "is_org_admin": current_user.is_org_admin,
            "organization_id": current_user.organization_id,
            "branch_id": current_user.branch_id,
            "designation": current_user.designation,
            "inactive": current_user.inactive
        },
        
        # Organization info
        "organization": org_data,
        
        # 🔥 Menus (ALL for org_admin)
        "menus": menus,
        
        # 🔥 Permissions (FULL for org_admin)
        "permissions": permissions,
        
        # Access level
        "access_level": "full" if has_full_access else "limited"
    }


# ============================================
# REFRESH TOKEN
# ============================================
@router.post("/refresh")
async def refresh_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✅ Refresh access token for logged-in user
    - Validates organization status
    - Generates new token
    """
    
    # Check organization status
    if current_user.organization_id:
        try:
            await TenantLimitsMiddleware.check_organization_status(
                organization_id=current_user.organization_id,
                db=db
            )
        except HTTPException as e:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Cannot refresh token: {e.detail}"
            )
    
    # Generate new token
    new_token = create_access_token(data={"sub": str(current_user.id)})
    
    return {
        "access_token": new_token,
        "token_type": "bearer",
        "message": "Token refreshed successfully"
    }


# ============================================
# LOGOUT
# ============================================
@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    ✅ Logout endpoint (informational only)
    - Actual logout happens client-side by removing token
    - This endpoint can be used for audit logging
    """
    return {
        "message": f"User {current_user.email} logged out successfully",
        "user_id": current_user.id
    }


# 🎯 Key Changes Based on Seeders:

## 1. **Role Hierarchy (By Name)**

# super_admin     → Platform-wide access (all organizations)
# org_admin       → Organization-wide access (their org only)
# manager         → Department/team level (role rights)
# employee        → Basic level (role rights)
