from sqlalchemy import Column,Integer,String,Numeric,DateTime,Boolean,func
from sqlalchemy.orm import relationship
from app.database import Base

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False) #basic, premium, enterprise
    description = Column(String(255), nullable=True)
    
    #Pricing
    price_monthly = Column(Numeric(10, 2), nullable=False)
    price_yearly = Column(Numeric(10, 2), nullable=True)

    #Limits
    branch_limit = Column(Integer, default=2)
    user_limit = Column(Integer, default=10)
    users_per_branch = Column(Integer, nullable=True)
    storage_limit_mb= Column(Integer, default=1000)  # Storage limit in MB

    #Features
    has_analytics=Column(Boolean, default=False)
    has_api_access=Column(Boolean, default=False)
    has_priority_support=Column(Boolean, default=False)
    has_whatsapp_notifications=Column(Boolean, default=False)
    has_custom_branding=Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),server_onupdate=func.now())
    created_by=Column(String(100), nullable=True)
    modified_by=Column(String(100), nullable=True)
    
    #Relationships
    organizations = relationship("Organization", back_populates="plan")