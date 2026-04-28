from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class SubscriptionPlanModule(Base):
    __tablename__ = "subscription_plan_modules"

    id = Column(Integer, primary_key=True, index=True)

    plan_id = Column(
        Integer,
        ForeignKey("subscription_plans.id", ondelete="CASCADE"),
        nullable=False
    )
    module_id = Column(
        Integer,
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("plan_id", "module_id", name="uq_plan_module"),
    )

    # relationships (optional but useful)
    plan = relationship("SubscriptionPlan", backref="plan_modules")
    module = relationship("Module", backref="module_plans")
