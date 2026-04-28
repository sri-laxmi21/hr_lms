from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    
    # Payment Gateway Info
    payment_gateway = Column(String(20), nullable=False)  # razorpay, stripe
    gateway_customer_id = Column(String(100), nullable=True)  # Customer ID from gateway
    gateway_payment_method_id = Column(String(100), nullable=True)  # Payment method ID from gateway
    
    # Payment Method Details
    method_type = Column(String(50), nullable=False)  # card, upi, netbanking, wallet
    
    # Card Details (if applicable)
    card_last4 = Column(String(4), nullable=True)
    card_brand = Column(String(20), nullable=True)  # visa, mastercard, amex, etc.
    card_expiry_month = Column(Integer, nullable=True)
    card_expiry_year = Column(Integer, nullable=True)
    
    # UPI/Other Details
    upi_id = Column(String(100), nullable=True)
    bank_name = Column(String(100), nullable=True)
    
    # Status
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Audit Fields
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="payment_methods")
