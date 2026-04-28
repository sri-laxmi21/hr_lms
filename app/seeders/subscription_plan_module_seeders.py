from sqlalchemy.orm import Session
from app.models.subscription_plans_m import SubscriptionPlan
from app.models.module_m import Module
from app.models.subscription_plan_module_m import SubscriptionPlanModule

def seed_subscription_plan_modules(db: Session):

    plans = {p.name.lower(): p.id for p in db.query(SubscriptionPlan).all()}
    modules = {m.name.lower(): m.id for m in db.query(Module).all()}

    plan_module_map = {
    "basic trial": ["base", "hrms"],   # ✅ ADD THIS
    "basic": ["base", "hrms"],
    "premium": ["base", "hrms", "lms"],
    "enterprise": ["base", "hrms", "lms", "hiring"],
}


    for plan_name, module_names in plan_module_map.items():
        plan_id = plans.get(plan_name)

        if not plan_id:
            continue

        for module_name in module_names:
            module_id = modules.get(module_name)
            if not module_id:
                continue

            exists = (
                db.query(SubscriptionPlanModule)
                .filter_by(plan_id=plan_id, module_id=module_id)
                .first()
            )

            if not exists:
                db.add(
                    SubscriptionPlanModule(
                        plan_id=plan_id,
                        module_id=module_id
                    )
                )
    db.commit()

    print("Subscription plan-module mapping seeded successfully")
