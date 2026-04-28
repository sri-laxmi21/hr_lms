from sqlalchemy import Column, Integer, String,DateTime,func,Boolean,Numeric,ForeignKey,Date
from sqlalchemy.orm import relationship
from app.database import Base

class Payment(Base):
    __tablename__="payments"
    
    id=Column(Integer,primary_key=True,index=True)
    organization_id=Column(Integer,ForeignKey("organizations.id",ondelete="CASCADE"))
    payment_method_id=Column(Integer,ForeignKey("payment_methods.id"),nullable=True)
    
    amount=Column(Numeric(10,2),nullable=False)
    currency=Column(String(3),default="INR")  # INR, USD, etc.
    payment_type=Column(String(50),nullable=False) #subscription,addon etc
    payment_method=Column(String(50),nullable=True) #credit card, paypal etc
    billing_cycle=Column(String(20),nullable=True)  # monthly, yearly
    
    # Payment Gateway Integration
    payment_gateway=Column(String(20),nullable=True)  # razorpay, stripe
    gateway_payment_id=Column(String(100),nullable=True)  # Payment ID from gateway
    gateway_order_id=Column(String(100),nullable=True,unique=True)  # Order ID from gateway
    gateway_signature=Column(String(255),nullable=True)  # Payment signature for verification
    
    transaction_id=Column(String(100),nullable=True,unique=True)
    payment_status=Column(String(20),default="pending") #completed,failed,pending,refunded
    payment_date=Column(Date,nullable=True)
    
    description=Column(String(255),nullable=True)
    gateway_metadata=Column(String(1000),nullable=True)  # JSON string for additional gateway data
    
    created_at=Column(DateTime,server_default=func.now())
    updated_at=Column(DateTime,server_default=func.now(),server_onupdate=func.now())
    
    created_by=Column(String(100),nullable=True)
    modified_by=Column(String(100),nullable=True)
    
    #Relationships
    organization=relationship("Organization",back_populates="payments")
    payment_method_rel=relationship("PaymentMethod", foreign_keys=[payment_method_id])