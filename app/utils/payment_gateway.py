"""
Payment Gateway Integration Utilities
Supports Razorpay and Stripe payment gateways
"""

import razorpay
import hmac
import hashlib
from typing import Dict, Optional, Tuple
from decimal import Decimal
from app.config import settings


class RazorpayClient:
    """Razorpay payment gateway integration"""
    
    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    def create_order(self, amount: Decimal, currency: str = "INR", receipt: str = None, 
                     notes: Dict = None) -> Dict:
        """
        Create a Razorpay order
        
        Args:
            amount: Amount in currency (will be converted to paise)
            currency: Currency code (default: INR)
            receipt: Receipt ID for reference
            notes: Additional notes/metadata
        
        Returns:
            Dict with order details including order_id
        """
        amount_paise = int(amount * 100)  # Convert to paise
        
        order_data = {
            "amount": amount_paise,
            "currency": currency,
            "receipt": receipt or f"order_{hash(str(amount))}",
            "notes": notes or {}
        }
        
        order = self.client.order.create(data=order_data)
        return order
    
    def verify_payment_signature(self, payment_id: str, order_id: str, signature: str) -> bool:
        """
        Verify Razorpay payment signature
        
        Args:
            payment_id: Razorpay payment ID
            order_id: Razorpay order ID
            signature: Payment signature from Razorpay
        
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
    
    def get_payment_details(self, payment_id: str) -> Dict:
        """Get payment details from Razorpay"""
        return self.client.payment.fetch(payment_id)
    
    def create_customer(self, name: str, email: str, contact: str = None) -> Dict:
        """Create a customer in Razorpay"""
        customer_data = {
            "name": name,
            "email": email
        }
        if contact:
            customer_data["contact"] = contact
        
        return self.client.customer.create(data=customer_data)
    
    def verify_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)


class StripeClient:
    """Stripe payment gateway integration (placeholder for future implementation)"""
    
    def __init__(self):
        # TODO: Initialize Stripe client when needed
        pass
    
    def create_order(self, amount: Decimal, currency: str = "USD") -> Dict:
        """Create a Stripe payment intent"""
        raise NotImplementedError("Stripe integration coming soon")
    
    def verify_payment(self, payment_intent_id: str) -> bool:
        """Verify Stripe payment"""
        raise NotImplementedError("Stripe integration coming soon")


class PaymentGatewayFactory:
    """Factory to get the appropriate payment gateway client"""
    
    @staticmethod
    def get_client(gateway: str = None):
        """
        Get payment gateway client
        
        Args:
            gateway: Gateway name ('razorpay' or 'stripe'). 
                    If None, uses default from settings.
        
        Returns:
            Payment gateway client instance
        """
        gateway = gateway or settings.PAYMENT_GATEWAY
        
        if gateway.lower() == "razorpay":
            return RazorpayClient()
        elif gateway.lower() == "stripe":
            return StripeClient()
        else:
            raise ValueError(f"Unsupported payment gateway: {gateway}")
