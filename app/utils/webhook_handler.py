"""
Webhook Handler for Payment Gateway Events
Processes webhook events from Razorpay and Stripe
"""

import json
from typing import Dict
from sqlalchemy.orm import Session
from datetime import date

from app.models.payment_m import Payment
from app.models.organization_m import Organization
from app.utils.payment_gateway import PaymentGatewayFactory
from app.config import settings


class WebhookHandler:
    """Handles webhook events from payment gateways"""
    
    @staticmethod
    def verify_webhook_signature(payload: str, signature: str, gateway: str = "razorpay") -> bool:
        """
        Verify webhook signature
        
        Args:
            payload: Raw webhook payload
            signature: Signature from webhook headers
            gateway: Payment gateway name
        
        Returns:
            True if signature is valid
        """
        client = PaymentGatewayFactory.get_client(gateway)
        
        if gateway == "razorpay":
            return client.verify_webhook_signature(
                payload, 
                signature, 
                settings.RAZORPAY_WEBHOOK_SECRET
            )
        
        return False
    
    @staticmethod
    def handle_payment_success(db: Session, event_data: Dict) -> bool:
        """
        Handle successful payment event
        
        Args:
            db: Database session
            event_data: Event data from webhook
        
        Returns:
            True if handled successfully
        """
        try:
            payment_entity = event_data.get("payload", {}).get("payment", {}).get("entity", {})
            payment_id = payment_entity.get("id")
            order_id = payment_entity.get("order_id")
            amount = payment_entity.get("amount", 0) / 100  # Convert from paise
            
            # Find payment record
            payment = db.query(Payment).filter(
                Payment.gateway_order_id == order_id
            ).first()
            
            if not payment:
                print(f"Payment not found for order_id: {order_id}")
                return False
            
            # Update payment status
            payment.payment_status = "completed"
            payment.gateway_payment_id = payment_id
            payment.payment_date = date.today()
            
            # Update organization
            organization = db.query(Organization).filter(
                Organization.id == payment.organization_id
            ).first()
            
            if organization:
                organization.last_payment_date = date.today()
                organization.total_amount_paid += payment.amount
            
            db.commit()
            
            # TODO: Send email notification
            # TODO: Activate subscription if it was a subscription payment
            
            return True
            
        except Exception as e:
            print(f"Error handling payment success: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def handle_payment_failed(db: Session, event_data: Dict) -> bool:
        """
        Handle failed payment event
        
        Args:
            db: Database session
            event_data: Event data from webhook
        
        Returns:
            True if handled successfully
        """
        try:
            payment_entity = event_data.get("payload", {}).get("payment", {}).get("entity", {})
            order_id = payment_entity.get("order_id")
            error_description = payment_entity.get("error_description", "Payment failed")
            
            # Find payment record
            payment = db.query(Payment).filter(
                Payment.gateway_order_id == order_id
            ).first()
            
            if not payment:
                print(f"Payment not found for order_id: {order_id}")
                return False
            
            # Update payment status
            payment.payment_status = "failed"
            payment.description = error_description
            
            db.commit()
            
            # TODO: Send email notification about failed payment
            # TODO: Handle grace period logic
            
            return True
            
        except Exception as e:
            print(f"Error handling payment failure: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def handle_subscription_renewal(db: Session, event_data: Dict) -> bool:
        """
        Handle subscription renewal event (for auto-renewals)
        
        Args:
            db: Database session
            event_data: Event data from webhook
        
        Returns:
            True if handled successfully
        """
        # TODO: Implement auto-renewal logic
        # This would be triggered by a scheduled job or recurring payment webhook
        return True
    
    @staticmethod
    def process_webhook(db: Session, event: str, payload: Dict, gateway: str = "razorpay") -> bool:
        """
        Process webhook event
        
        Args:
            db: Database session
            event: Event type
            payload: Event payload
            gateway: Payment gateway name
        
        Returns:
            True if processed successfully
        """
        event_handlers = {
            "payment.captured": WebhookHandler.handle_payment_success,
            "payment.failed": WebhookHandler.handle_payment_failed,
            "subscription.charged": WebhookHandler.handle_subscription_renewal,
        }
        
        handler = event_handlers.get(event)
        
        if handler:
            return handler(db, payload)
        else:
            print(f"No handler for event: {event}")
            return False
