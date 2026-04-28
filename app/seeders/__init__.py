from app.database import SessionLocal

def run_all_seeders():
    print("Running seeders...")
    # Trigger model registration
    import app.models
    db = SessionLocal()

    try:
        # Import inside function to avoid circular imports
        from app.seeders.menu_seeder import seed_menus
        from app.seeders.week_day_seeders import seed_weekdays
        from app.seeders.role_seeder import seed_roles
        from app.seeders.role_right_seeder import seed_role_rights
        from app.seeders.super_admin import seed_super_admin
        from app.seeders.module_seeders import seed_modules
        from app.seeders.subscription_plan_module_seeders import seed_subscription_plan_modules
        
        # IMPORTANT ORDER
        seed_modules(db)          # Modules first (dependency for menus)
        seed_roles(db)            # Roles next
        seed_menus(db)            # Menus 
        seed_weekdays(db)         # Week master
        seed_role_rights(db)      # Depends on roles + menus
        seed_super_admin(db)      # Depends on roles
        seed_subscription_plan_modules(db)     # Depends on modules
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()
    
    print("All seeders executed successfully")