"""
Subscription Management Utilities
Handles subscription lifecycle, trial periods, and plan changes
"""

from datetime import date, timedelta
from typing import Optional, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.organization_m import Organization
from app.models.subscription_plans_m import SubscriptionPlan
from app.models.payment_m import Payment


class SubscriptionManager:
    """Manages subscription lifecycle and operations"""
    
    @staticmethod
    def check_trial_status(organization: Organization) -> dict:
        """
        Check trial period status for an organization
        
        Returns:
            Dict with trial status information
        """
        if not organization.is_trial:
            return {
                "is_trial": False,
                "trial_expired": False,
                "trial_days_remaining": None,
                "can_convert_to_paid": True
            }
        
        if not organization.trial_end_date:
            return {
                "is_trial": True,
                "trial_expired": False,
                "trial_days_remaining": organization.trial_days,
                "can_convert_to_paid": True
            }
        
        today = date.today()
        days_remaining = (organization.trial_end_date - today).days
        trial_expired = today > organization.trial_end_date
        
        return {
            "is_trial": True,
            "trial_start_date": organization.trial_start_date,
            "trial_end_date": organization.trial_end_date,
            "trial_expired": trial_expired,
            "trial_days_remaining": max(0, days_remaining),
            "can_convert_to_paid": not trial_expired or days_remaining >= -7  # 7 day grace period
        }
    
    @staticmethod
    def activate_subscription(
        db: Session,
        organization: Organization,
        plan: SubscriptionPlan,
        billing_cycle: str,
        payment: Payment
    ) -> Organization:
        """
        Activate paid subscription for an organization
        
        Args:
            db: Database session
            organization: Organization to activate
            plan: Subscription plan
            billing_cycle: 'monthly' or 'yearly'
            payment: Payment record
        
        Returns:
            Updated organization
        """
        today = date.today()
        
        # Calculate subscription end date
        if billing_cycle == "monthly":
            end_date = today + timedelta(days=30)
        else:  # yearly
            end_date = today + timedelta(days=365)
        
        # Update organization
        organization.is_trial = False
        organization.subscription_status = "active"
        organization.subscription_start_date = today
        organization.subscription_end_date = end_date
        organization.plan_id = plan.id
        organization.next_billing_date = end_date
        organization.last_payment_date = today
        organization.total_amount_paid += payment.amount
        
        # Apply plan limits
        organization.branch_limit = plan.branch_limit
        organization.user_limit = plan.user_limit
        organization.storage_limit_mb = plan.storage_limit_mb
        
        db.commit()
        db.refresh(organization)
        
        return organization
    
    @staticmethod
    def upgrade_subscription(
        db: Session,
        organization: Organization,
        new_plan: SubscriptionPlan,
        current_plan: SubscriptionPlan
    ) -> Tuple[Organization, Decimal]:
        """
        Upgrade subscription to a higher plan
        
        Returns:
            Tuple of (updated organization, prorated amount to charge)
        """
        # Calculate prorated amount
        if organization.subscription_end_date and organization.next_billing_date:
            days_remaining = (organization.subscription_end_date - date.today()).days
            total_days = (organization.subscription_end_date - organization.subscription_start_date).days
            
            if total_days > 0:
                # Refund for unused portion of current plan
                unused_amount = (current_plan.price_monthly / total_days) * days_remaining
                
                # Charge for new plan (prorated)
                new_plan_amount = (new_plan.price_monthly / total_days) * days_remaining
                
                prorated_amount = new_plan_amount - unused_amount
            else:
                prorated_amount = new_plan.price_monthly
        else:
            prorated_amount = new_plan.price_monthly
        
        # Update organization
        organization.plan_id = new_plan.id
        organization.branch_limit = new_plan.branch_limit
        organization.user_limit = new_plan.user_limit
        organization.storage_limit_mb = new_plan.storage_limit_mb
        
        db.commit()
        db.refresh(organization)
        
        return organization, max(Decimal('0'), prorated_amount)
    
    @staticmethod
    def downgrade_subscription(
        db: Session,
        organization: Organization,
        new_plan: SubscriptionPlan,
        effective_immediately: bool = False
    ) -> Organization:
        """
        Downgrade subscription to a lower plan
        
        Args:
            db: Database session
            organization: Organization to downgrade
            new_plan: New subscription plan
            effective_immediately: If True, apply immediately. Otherwise, at end of billing period.
        
        Returns:
            Updated organization
        """
        if effective_immediately:
            organization.plan_id = new_plan.id
            organization.branch_limit = new_plan.branch_limit
            organization.user_limit = new_plan.user_limit
            organization.storage_limit_mb = new_plan.storage_limit_mb
        else:
            # Schedule downgrade for next billing date
            # This would typically be stored in a separate table for pending changes
            # For now, we'll apply immediately
            organization.plan_id = new_plan.id
            organization.branch_limit = new_plan.branch_limit
            organization.user_limit = new_plan.user_limit
            organization.storage_limit_mb = new_plan.storage_limit_mb
        
        db.commit()
        db.refresh(organization)
        
        return organization
    
    @staticmethod
    def cancel_subscription(
        db: Session,
        organization: Organization,
        cancel_immediately: bool = False
    ) -> Organization:
        """
        Cancel subscription
        
        Args:
            db: Database session
            organization: Organization to cancel
            cancel_immediately: If True, cancel now. Otherwise, at end of billing period.
        
        Returns:
            Updated organization
        """
        if cancel_immediately:
            organization.subscription_status = "cancelled"
            organization.is_active = False
        else:
            # Mark for cancellation at end of billing period
            organization.subscription_status = "cancelled_pending"
        
        db.commit()
        db.refresh(organization)
        
        return organization
    
    @staticmethod
    def check_feature_access(organization: Organization, feature: str) -> bool:
        """
        Check if organization has access to a specific feature
        
        Args:
            organization: Organization to check
            feature: Feature name (e.g., 'analytics', 'api_access')
        
        Returns:
            True if organization has access, False otherwise
        """
        if not organization.plan:
            return False
        
        feature_map = {
            "analytics": organization.plan.has_analytics,
            "api_access": organization.plan.has_api_access,
            "priority_support": organization.plan.has_priority_support,
            "whatsapp_notifications": organization.plan.has_whatsapp_notifications,
            "custom_branding": organization.plan.has_custom_branding
        }
        
        return feature_map.get(feature, False)
    
    @staticmethod
    def apply_plan_limits(db: Session, organization: Organization, plan: SubscriptionPlan):
        """Apply plan limits to organization"""
        organization.branch_limit = plan.branch_limit
        organization.user_limit = plan.user_limit
        organization.storage_limit_mb = plan.storage_limit_mb
        
        db.commit()
        db.refresh(organization)
