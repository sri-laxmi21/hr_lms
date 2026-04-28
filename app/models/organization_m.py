# app/models/organization_m.py
from sqlalchemy import Column, Integer, String, DateTime, func,Date,Boolean,Numeric,ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    
    #Subscription & Billing \
    plan_id = Column(Integer,ForeignKey("subscription_plans.id") ,nullable=True)  # FK to SubscriptionPlan
    subscription_status=Column(String(20), default="trial")  # trial, active, expired, suspended
    subscription_start_date=Column(Date, nullable=True)
    subscription_end_date=Column(Date, nullable=True)
    
    # Trial Period Tracking
    is_trial = Column(Boolean, default=True)
    trial_start_date = Column(Date, nullable=True)
    trial_end_date = Column(Date, nullable=True)
    trial_days = Column(Integer, default=14)  # Default trial period in days
    
    #Usage Tracking
    branch_limit=Column(Integer,default=2)
    current_branches=Column(Integer,default=0)
    user_limit=Column(Integer,default=10)
    current_users=Column(Integer,default=0)
    storage_limit_mb=Column(Integer,default=1000)
    current_storage_mb=Column(Integer,default=0)
    
    #Billing
    last_payment_date=Column(Date,nullable=True)
    next_billing_date=Column(Date,nullable=True)
    total_amount_paid=Column(Numeric(10,2),default=0)
    
    #Status & Contact
    is_active=Column(Boolean,default=True)
    contact_email=Column(String(100),nullable=True)
    contact_phone=Column(String(20),nullable=True)
    
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),server_onupdate=func.now(), nullable=False)

    created_by=Column(String(100),nullable=True)
    modified_by=Column(String(100),nullable=True)
    
    # Relationships
    plan=relationship("SubscriptionPlan",back_populates="organizations")
    branches = relationship("Branch",back_populates="organization",cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="organization", cascade="all, delete-orphan")
    add_ons = relationship("OrganizationAddOn", back_populates="organization", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="organization", cascade="all, delete-orphan")
    payment_methods = relationship("PaymentMethod", back_populates="organization", cascade="all, delete-orphan")
    job_postings = relationship("JobPosting", back_populates="organization")
