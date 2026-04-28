from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional

from app.database import get_db
from app.schema.user_schema import (
    UserCreate,
    UserOrganizationResponse, 
    UserResponse, 
    UserDetailResponse,
    UserUpdate
)

from app.models.user_m import User
from app.models.role_m import Role
from app.models.branch_m import Branch
from app.models.organization_m import Organization
from app.models.salary_structure_m import SalaryStructure
from app.utils.utils import hash_password
from app.dependencies import get_current_user
from app.middleware.tenant_limits import TenantLimitsMiddleware

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/users", tags=["Users"])
USERS_MENU_ID = 3 # Updated to match your menu seeder



# ============================================================
# ROLE VALIDATION HELPER
# ============================================================
def validate_role_assignment(current_user: User, target_role: Role) -> bool:
    """
    ✅ Validate if current user can assign a specific role
    
    Rules:
    - super_admin: Can assign ANY role (including super_admin)
    - org_admin: Can assign org_admin, manager, employee (NOT super_admin)
    - manager: Can assign employee only (NOT org_admin or manager)
    - employee: Cannot assign any roles
    """
    current_role = current_user.role.name.lower() if current_user.role else None
    target_role_name = target_role.name.lower()

    # Super admin can assign any role
    if current_role == "super_admin":
        return True

    # Org admin can assign: org_admin, manager, employee (NOT super_admin)
    if current_user.is_org_admin or current_role == "org_admin":
        return target_role_name in ["org_admin", "manager", "employee"]
    
    # Manager can only assign employee role
    if current_role == "manager":
        return target_role_name == "employee"

    return False


# ============================================================
# CREATE USER
# ============================================================
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_create_permission(USERS_MENU_ID))
):
    """✅ Create a new user within the current organization
    - Org admins can create: org_admin, manager, employee
    - Managers can create: employee only
    - Checks user limit before creating
    - Auto-assigns organization from current user
    - Updates organization user count"""

# 🔒 Ensure user has an organization
    if not current_user.organization_id:
        raise HTTPException(403, "You must belong to an organization to create users")

    # ✅ Check user limit for organization
    await TenantLimitsMiddleware.check_user_limit(
        organization_id=current_user.organization_id,
        db=db
    )

    # Check duplicate email (within same organization for better multi-tenancy)
    existing_user = db.query(User).filter(
        and_(
            User.email == payload.email.lower(),
            User.organization_id == current_user.organization_id
        )
    ).first()

    if existing_user:
        raise HTTPException(400, "Email already exists in your organization")

    # 🔥 Verify role exists and validate assignment
    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(400, "Invalid role_id")

    # 🔥 Validate if current user can assign this role
    if not validate_role_assignment(current_user, role):
        raise HTTPException(403, f"You cannot assign role '{role.name}'")

    # Verify branch belongs to same organization (if provided)
    if payload.branch_id:
        branch = db.query(Branch).filter(
            and_(
                Branch.id == payload.branch_id,
                Branch.organization_id == current_user.organization_id
            )
        ).first()

        if not branch:
            raise HTTPException(400, "Branch does not belong to your organization")

    # SALARY STRUCTURE VALIDATION (✔ organization_id removed)
    if payload.salary_structure_id:
        structure = db.query(SalaryStructure).filter(
            SalaryStructure.id == payload.salary_structure_id
        ).first()

        if not structure:
            raise HTTPException(400, "Invalid salary_structure_id")


    # 🔥 Force organization_id to be current user's organization
    user_data = payload.dict(exclude={"password"})
    user_data["hashed_password"] = hash_password(payload.password)
    user_data["organization_id"] = current_user.organization_id
    user_data["created_by"] = f"{current_user.first_name} {current_user.last_name}"


# 🔥 Set is_org_admin flag based on role
    # Only set to True if role is "org_admin" AND current user has permission
    user_data["is_org_admin"] = (
        role.name.lower() == "org_admin" and
        (current_user.is_org_admin or current_user.role.name.lower() == "super_admin")
    )

    new_user = User(**user_data)

    db.add(new_user)
    db.commit()

    # ✅ Update organization user count
    TenantLimitsMiddleware.update_user_count(
        organization_id=current_user.organization_id,
        db=db,
        increment=True
    )

    db.refresh(new_user)
    return UserResponse.model_validate(new_user)



# ============================================================
# GET USERS OF MY ORGANIZATION (ORG ADMIN VIEW)
# ============================================================
@router.get(
    "/my-organization",
    response_model=List[UserOrganizationResponse],
    dependencies=[Depends(require_view_permission(USERS_MENU_ID))]
)
def get_users_of_my_organization(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not linked to any organization"
        )

    users = (
        db.query(User)
        .options(
            joinedload(User.branch), # type: ignore
            joinedload(User.role), # type: ignore
            joinedload(User.salary_structure), # type: ignore
        )
        .filter(User.organization_id == current_user.organization_id)
        .all()
    )

    response = []

    for u in users:
        salary_structure_name = None

        if u.salary_structure:
            # ✅ SAFE ATTRIBUTE ACCESS (NO AttributeError EVER)
            salary_structure_name = (
                getattr(u.salary_structure, "name", None)
                or getattr(u.salary_structure, "title", None)
                or getattr(u.salary_structure, "structure_name", None)
                or getattr(u.salary_structure, "code", None)
            )

        response.append(
            UserOrganizationResponse(
                id=u.id,
                first_name=u.first_name,
                last_name=u.last_name,
                email=u.email,
                phone=None, # phone not in User model
                is_active=not u.inactive,

                organization_id=u.organization_id,

                branch_id=u.branch_id,
                branch_name=u.branch.name if u.branch else None,

                role_id=u.role_id,
                role_name=u.role.name if u.role else None,

                salary_structure_id=u.salary_structure_id,
                salary_structure_name=salary_structure_name,

                created_at=u.created_at,
            )
        )

    return response



# ============================================================
# AVAILABLE ROLES TO ASSIGN
# ============================================================
@router.get("/available-roles")
async def get_available_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """  ✅ Get list of roles that current user can assign to new users
    
    Returns different roles based on current user's role:
    - super_admin: all roles
    - org_admin: org_admin, manager, employee
    - manager: employee only
    - employee: none """

    current_role = current_user.role.name.lower() if current_user.role else None


    # Define allowed roles based on current user's role
    if current_role == "super_admin":
        allowed = ["super_admin", "org_admin", "manager", "employee"]
    elif current_user.is_org_admin or current_role == "org_admin":
        allowed = ["org_admin", "manager", "employee"]
    elif current_role == "manager":
        allowed = ["employee"]
    else:
        allowed = []

     # Fetch roles from database
    if not allowed:
        return []

    roles = db.query(Role).filter(Role.name.in_(allowed)).all()

    return [
        {
            "id": r.id,
            "name": r.name,
            "display_name": r.name.replace("_", " ").title()
        }
        for r in roles
    ]


# ============================================================
# GET CURRENT USER PROFILE
# ============================================================
@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    """ ✅ Get current logged-in user's profile """
  
    user = db.query(User).options(
        selectinload(User.role),
        selectinload(User.branch),
        selectinload(User.organization),
        selectinload(User.department),
        selectinload(User.salary_structure)
    ).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(404, "User not found")

    return UserDetailResponse(
        **user.__dict__,
        role_name=user.role.name if user.role else None,
        branch_name=user.branch.name if user.branch else None,
        organization_name=user.organization.name if user.organization else None,
        department_name=user.department.name if user.department else None,
        salary_structure_name=user.salary_structure.name if user.salary_structure else None
    )


# ============================================================
# GET USER BY ID
# ============================================================
@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_view_permission(USERS_MENU_ID))
):
    
    """ ✅ Get user by ID (must be in same organization) """

    user = db.query(User).options(
        selectinload(User.role),
        selectinload(User.branch),
        selectinload(User.organization),
        selectinload(User.department),
        selectinload(User.salary_structure)
    ).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")


 # 🔒 Check organization access
    if current_user.role.name.lower() != "super_admin" and \
            user.organization_id != current_user.organization_id:
        raise HTTPException(403, "Unauthorized")

    return UserDetailResponse(
        **user.__dict__,
        role_name=user.role.name if user.role else None,
        branch_name=user.branch.name if user.branch else None,
        organization_name=user.organization.name if user.organization else None,
        department_name=user.department.name if user.department else None,
        salary_structure_name=user.salary_structure.name if user.salary_structure else None
    )


# ============================================================
# UPDATE USER
# ============================================================
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(USERS_MENU_ID))
):
    
    """ ✅ Update user details (must be in same organization)
    - Validates role changes based on current user's permissions """

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(404, "User not found")

    # 🔒 Check organization access
    if current_user.role.name.lower() != "super_admin" and \
            db_user.organization_id != current_user.organization_id:
        raise HTTPException(403, "Unauthorized")


    # 🔥 Validate role change if role_id is being updated
    if payload.role_id and payload.role_id != db_user.role_id:
        new_role = db.query(Role).filter(Role.id == payload.role_id).first()
        if not new_role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id")


        # Validate role assignment permission
        if not validate_role_assignment(current_user, new_role):
            raise HTTPException( status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission to assign '{new_role.name}' role")

# Update is_org_admin flag if role is changing to/from org_admin
        db_user.is_org_admin = new_role.name.lower() == "org_admin"
        db_user.is_org_admin = True   
    elif db_user.role and db_user.role.name.lower() == "org_admin":
            # Changing from org_admin to another role
            db_user.is_org_admin = False

    # Verify branch belongs to same organization (if changing)
    if payload.branch_id and payload.branch_id != db_user.branch_id:
        branch = db.query(Branch).filter(
            and_(
                Branch.id == payload.branch_id,
                Branch.organization_id == db_user.organization_id
            )
        ).first()

        if not branch:
            raise HTTPException(400, "Branch does not belong to organization")

    # SALARY STRUCTURE UPDATE (✔ organization check removed)
    if payload.salary_structure_id:
        structure = db.query(SalaryStructure).filter(
            SalaryStructure.id == payload.salary_structure_id
        ).first()

        if not structure:
            raise HTTPException(400, "Invalid salary_structure_id")

        db_user.salary_structure_id = payload.salary_structure_id

    # 🔒 Prevent organization_id change (can't move users between orgs)
    update_data = payload.dict(exclude_unset=True, exclude={"organization_id"})
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db_user.modified_by = f"{current_user.first_name} {current_user.last_name}"

    db.commit()
    db.refresh(db_user)
    # return UserResponse.from_orm(db_user)

    return UserResponse.model_validate(db_user)


# ============================================================
# DELETE USER
# ============================================================
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delete_permission(USERS_MENU_ID))
):
    """ ✅ Delete user (must be in same organization)
    - Decrements organization user count """

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")


    # 🔒 Check organization access
    if current_user.role.name.lower() != "super_admin" and \
            user.organization_id != current_user.organization_id:
        raise HTTPException(403, "Unauthorized")


    # 🔒 Prevent deleting org admin (last admin protection)
    if user.is_org_admin:
        count = db.query(User).filter(
            and_(
                User.organization_id == user.organization_id,
                User.is_org_admin == True
            )
        ).count()

        if count <= 1:
            raise HTTPException(400, "Cannot delete last org admin")

    org_id = user.organization_id

    db.delete(user)
    db.commit()


    # ✅ Update organization user count
    TenantLimitsMiddleware.update_user_count(
        organization_id=org_id,
        db=db,
        increment=False
    )

    return None


# ============================================================
# ASSIGN SHIFT ROSTER TO ROLE
# ============================================================
@router.put("/assign-shift/{role_id}/{shift_roster_id}")
async def assign_shift_to_role(
    role_id: int,
    shift_roster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(USERS_MENU_ID))
):
    """     ✅ Assign shift roster to all users of a role (within current organization) """

    if not current_user.organization_id:
        raise HTTPException(403, "No organization assigned")


    # Get users of this role in current organization only
    users = db.query(User).filter(
        and_(
            User.role_id == role_id,
            User.organization_id == current_user.organization_id
        )
    ).all()

    if not users:
        raise HTTPException(404, "No users found")

    for user in users:
        user.shift_roster_id = shift_roster_id
        user.modified_by = f"{current_user.first_name} {current_user.last_name}"

    db.commit()
    # return {"message": "Shift roster assigned", "total_updated_users": len(users)}

    return {
        "message": "Shift roster assigned",
        "role_id": role_id,
        "shift_roster_id": shift_roster_id,
        "updated_users": len(users)
    }


# ============================================================
# ASSIGN SHIFT ROSTER TO SINGLE USER
# ============================================================
@router.patch("/update-shift/{user_id}/{shift_roster_id}")
async def update_user_shift_roster(
    user_id: int,
    shift_roster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_edit_permission(USERS_MENU_ID))
):
    """     ✅ Update shift roster for a single user (must be in same organization)
"""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")


    # 🔒 Check organization access
    if current_user.role.name.lower() != "super_admin" and \
            user.organization_id != current_user.organization_id:
        raise HTTPException(403, "Unauthorized")

    user.shift_roster_id = shift_roster_id
    user.modified_by = f"{current_user.first_name} {current_user.last_name}"

    db.commit()
    db.refresh(user)

    return {
        "message": "Shift roster updated",
        "user_id": user_id,
        "shift_roster_id": shift_roster_id
    }


# ============================================================
# MAKE USER ORG ADMIN
# ============================================================
@router.patch("/{user_id}/make-org-admin")
async def make_user_org_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ ✅ Promote user to organization admin
    Only existing org admin or super admin can do this"""


    # Check if current user has permission
    if not (current_user.is_org_admin or current_user.role.name == "super_admin"):
        raise HTTPException(403, "Only org admins can promote users")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")


    # Must be in same organization
    if current_user.role.name != "super_admin" and \
            user.organization_id != current_user.organization_id:
        raise HTTPException(403, "Target must be in your organization")

    user.is_org_admin = True
    user.modified_by = f"{current_user.first_name} {current_user.last_name}"

    db.commit()
    db.refresh(user)

    return {
        "message": "User promoted to org admin",
        "user_id": user_id
    }