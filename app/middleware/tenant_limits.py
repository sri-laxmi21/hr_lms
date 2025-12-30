from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from app.models.organization_m import Organization
from app.models.user_m import User
from datetime import date
from typing import Optional

class TenantLimitsMiddleware:
    """
    Middleware to check organization limits before allowing actions.
    Prevents users from exceeding their subscription limits.
    """
    @staticmethod
    async def check_organization_status(organization_id:int,db:Session) -> Organization:
        """
        ✅ Check if organization subscription is active and valid
        
        Args:
            organization_id: ID of the organization
            db: Database session
            
        Returns:
            Organization object if valid
            
        Raises:
            HTTPException: If org not found, subscription expired, or account suspended
        """
        org=db.query(Organization).filter(Organization.id==organization_id).first()
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        if not org.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your Organization account is suspended. Please contact support"
            )
            
        if org.subscription_status not in  ["active","trial"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Your organization subscription is {org.subscription_status}.Please Renew."
            )
            
        if org.subscription_end_date and org.subscription_end_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Your organization subscription has expired on {org.subscription_end_date}. Please Renew."
            )
            
        return org
    
    
    @staticmethod
    async def check_branch_limit(organization_id:int,db:Session,count_to_add:int=1) -> bool:
        """
        ✅ Check if organization can create more branches
        
        Args:
            organization_id: ID of the organization
            db: Database session
            count_to_add: Number of branches to add (default 1)
            
        Returns:
            True if within limit
            
        Raises:
            HTTPException: If branch limit exceeded
        """
        
        #First check org status
        org=await TenantLimitsMiddleware.check_organization_status(organization_id,db)
        
        # Calculate if adding new branches would exceed limit
        new_total=org.current_branches + count_to_add
        
        if new_total>org.branch_limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "message": "Branch limit exceeded",
                    "current": org.current_branches,
                    "limit": org.branch_limit,
                    "requested": count_to_add,
                    "suggestion": "Upgrade your plan or purchase additional branch add-ons to continue."
                }
            )
        return True
        
        
    @staticmethod
    async def check_user_limit(organization_id:int,db:Session,count_to_add:int=1) -> bool:
        """
        ✅ Check if organization can add more users
        
        Args:
            organization_id: ID of the organization
            db: Database session
            count_to_add: Number of users to add (default 1)
            
        Returns:
            True if within limit
            
        Raises:
            HTTPException: If user limit exceeded
        """
        #First check org status
        org= await TenantLimitsMiddleware.check_organization_status(organization_id,db)
        
        #Calculate adding new numbers would exceed limit
        new_total=org.current_users+count_to_add
        if new_total > org.user_limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "message": "User limit exceeded",
                    "current": org.current_users,
                    "limit": org.user_limit,
                    "requested": count_to_add,
                    "suggestion": "Upgrade your plan or purchase additional user add-ons to continue."
                }
            )
        return True
    
    
    @staticmethod
    async def check_storage_limit(organization_id:int,db:Session,file_size_mb:float) -> bool:
        """
        ✅ Check if organization has enough storage space
        
        Args:
            organization_id: ID of the organization
            db: Database session
            file_size_mb: Size of file to upload in MB
            
        Returns:
            True if within limit
            
        Raises:
            HTTPException: If storage limit exceeded
        """
        
        #First check org status
        org=await TenantLimitsMiddleware.check_organization_status(organization_id,db)
        
        #calculate if uploading would exceed storage limit
        new_total=org.current_storage_mb + file_size_mb
        
        if new_total > org.storage_limit_mb:
            available_space=org.storage_limit_mb - org.current_storage_mb
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "message": "Storage limit exceeded",
                    "current_mb": float(org.current_storage_mb),
                    "limit_mb": org.storage_limit_mb,
                    "requested_mb": file_size_mb,
                    "available_mb": max(0, available_space),
                    "suggestion": "Upgrade your plan or purchase additional storage to continue."
                }
            )
        return  True
    
    @staticmethod
    async def verify_user_belongs_to_org(user_id:int,organization_id:int,db:Session) -> bool:
        """
        ✅ Verify that user belongs to the specified organization
        
        Args:
            user_id: ID of the user
            organization_id: ID of the organization
            db: Database session
            
        Returns:
            True if user belongs to org
            
        Raises:
            HTTPException: If user doesn't belong to organization
        """
        user=db.query(User).filter(User.id==user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found"
            )
        if user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not belongs to this organization"
            )
        return True
    
    @staticmethod
    async def check_feature_access(organization_id:int, feature_name:str,db:Session) -> bool:
        """
        ✅ Check if organization has access to a specific feature
        
        Args:
            organization_id: ID of the organization
            feature_name: Name of the feature to check (e.g., 'has_analytics', 'has_api_access')
            db: Database session
            
        Returns:
            True if organization has access
            
        Raises:
            HTTPException: If feature not available in current plan
        """
        org = await TenantLimitsMiddleware.check_organization_status(organization_id,db)
        
        if not org.plan:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="No subscription plan assigned to this organization"
            )
        
        #Check if feature is enabled in the  plan
        has_feature=getattr(org.plan, feature_name, False)
        
        if not has_feature:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "message": f"Feature '{feature_name}' not available in your plan",
                    "current_plan": org.plan.name,
                    "suggestion": "Upgrade your plan to access this feature"
                }
            )
        
        return True
    @staticmethod
    def update_branch_count(organization_id:int,db:Session,increment:bool=True):
        """
        ✅ Update the current branch count for an organization
        
        Args:
            organization_id: ID of the organization
            db: Database session
            increment: True to add 1, False to subtract 1
        """
        org = db.query(Organization).filter(Organization.id==organization_id).first()
        if org:
            if increment:
                org.current_branches+=1
            else:
                org.current_branches = max(0,org.current_branches-1)
            db.commit()
            
    @staticmethod
    def update_user_count(organization_id:int,db:Session,increment:bool=True):
        """
        ✅ Update the current user count for an organization
        
        Args:
            organization_id: ID of the organization
            db: Database session
            increment: True to add 1, False to subtract 1
        """
        org = db.query(Organization).filter(Organization.id==organization_id).first()
        if org:
            if increment:
                org.current_users+=1
            else:
                org.current_users=max(0,org.current_users-1)
            db.commit()
            
            
    @staticmethod
    def update_storage_usage(organization_id:int,db:Session,size_mb:float,increment:bool=True):
        """
        ✅ Update the current storage usage for an organization
        
        Args:
            organization_id: ID of the organization
            db: Database session
            size_mb: Storage size in MB to add/remove
            increment: True to add, False to subtract
        """
        org = db.query(Organization).filter(Organization.id==organization_id).first()
        if org:
            if increment:
                org.current_storage_mb+=size_mb
            else:
                org.current_storage_mb=max(0,org.current_storage_mb-size_mb)
            db.commit()    