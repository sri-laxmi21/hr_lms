# app/seeders/seed_role_rights.py

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.role_right_m import RoleRight
from app.models.role_m import Role
from app.models.menu_m import Menu


def get_menu_by_name(db, name):
    """Get menu by name field (lowercase)"""
    return db.query(Menu).filter(Menu.name == name).first()


def get_role(db, name):
    """Get role by name"""
    return db.query(Role).filter(Role.name == name).first()


def seed_role_rights(db: Session):


    try:
        # ---------------------------------------------------------
        # 1. SUPER ADMIN -> FULL ACCESS (GLOBAL)
        # ---------------------------------------------------------
        super_admin = get_role(db, "super_admin")
        if not super_admin:
            print("[Error] super_admin role missing. Run seed_roles.py first.")
            return

        all_menus = db.query(Menu).all()
        print(f"Found {len(all_menus)} menus")

        for menu in all_menus:
            exists = db.query(RoleRight).filter_by(
                role_id=super_admin.id,
                menu_id=menu.id
            ).first()

            if not exists:
                db.add(RoleRight(
                    role_id=super_admin.id,
                    menu_id=menu.id,
                    can_view=True,
                    can_create=True,
                    can_edit=True,
                    can_delete=True,
                    created_by="System",
                    modified_by="System"
                ))
        
        print(f"Super Admin: Granted full access to all {len(all_menus)} menus")


        # ---------------------------------------------------------
        # 2. ORG ADMIN -> FULL ACCESS WITHIN THE ORG
        # ---------------------------------------------------------
        org_admin = get_role(db, "org_admin")
        if org_admin:
            for menu in all_menus:
                exists = db.query(RoleRight).filter_by(
                    role_id=org_admin.id,
                    menu_id=menu.id
                ).first()

                if not exists:
                    db.add(RoleRight(
                        role_id=org_admin.id,
                        menu_id=menu.id,
                        can_view=True,
                        can_create=True,
                        can_edit=True,
                        can_delete=True,
                        created_by="System",
                        modified_by="System"
                    ))
            
            print(f"Org Admin: Granted full access to all {len(all_menus)} menus")


        # ---------------------------------------------------------
        # 3. EMPLOYEE -> LIMITED ACCESS
        # ---------------------------------------------------------
        employee = get_role(db, "employee")
        if employee:
            # Use actual menu names from your seeder
            employee_allowed_menus = [
                "dashboard",           # Menu ID 1
                "attendance",          # Menu ID 44 (HRMS module)
                "leave_master",        # Menu ID 45 (for requesting leaves)
                "progress",            # Menu ID 37 (LMS - view own progress)
                "courses",             # Menu ID 31 (LMS - view courses)
                "videos",              # Menu ID 32 (LMS - watch videos)
                "enrollments",         # Menu ID 34 (view own enrollments)
            ]

            for menu_name in employee_allowed_menus:
                menu = get_menu_by_name(db, menu_name)
                if not menu:
                    print(f"⚠️  Menu '{menu_name}' not found, skipping...")
                    continue

                exists = db.query(RoleRight).filter_by(
                    role_id=employee.id,
                    menu_id=menu.id
                ).first()

                if not exists:
                    # Employees can view but not create/edit/delete
                    db.add(RoleRight(
                        role_id=employee.id,
                        menu_id=menu.id,
                        can_view=True,
                        can_create=False,  # Can't create
                        can_edit=False,    # Can't edit
                        can_delete=False,  # Can't delete
                        created_by="System",
                        modified_by="System"
                    ))
            
            print(f"Employee: Granted view access to {len(employee_allowed_menus)} menus")


        # ---------------------------------------------------------
        # 4. MANAGER -> MODERATE ACCESS
        # ---------------------------------------------------------
        manager = get_role(db, "manager")
        if manager:
            # Managers get more access than employees
            # Format: menu_name: (can_view, can_create, can_edit, can_delete)
            manager_access = {
                # Base Access
                "dashboard":            (True, False, False, False),
                
                # User Management (limited)
                "users":                (True, True, True, False),  # Can manage users
                
                # Organization
                "departments":          (True, True, True, False),  # Manage departments
                
                # HRMS Module
                "attendance":           (True, True, True, False),  # Manage attendance
                "shifts":               (True, True, True, False),  # Manage shifts
                "user_shifts":          (True, True, True, False),  # Assign shifts
                "shift_change_requests":(True, False, True, False), # Approve requests
                "leave_master":         (True, False, True, False), # Approve leaves
                "permissions_module":   (True, False, True, False), # Approve permissions
                
                # Payroll (view only)
                "payroll":              (True, False, False, False),
                "payroll_attendance":   (True, False, False, False),
                
                # Reports
                "reports":              (True, False, False, False),
                "attendance_reports":   (True, False, False, False),
                "daily_attendance":     (True, False, False, False),
                "monthly_attendance":   (True, False, False, False),
                
                # LMS Module (manage team learning)
                "courses":              (True, False, False, False),
                "videos":               (True, False, False, False),
                "enrollments":          (True, True, False, False),  # Enroll team
                "progress":             (True, False, False, False),  # View team progress
                 # Hiring Module — Manager can only create/post jobs
                "job_postings":         (True, True, False, False),
                # Hiring (if manager is hiring manager)
                "candidates":           (True, True, True, False),
                "candidate_documents":  (True, True, False, False),
            }

            for menu_name, perms in manager_access.items():
                menu = get_menu_by_name(db, menu_name)
                if not menu:
                    print(f"[Warning] Menu '{menu_name}' not found, skipping...")
                    continue

                can_view, can_create, can_edit, can_delete = perms

                exists = db.query(RoleRight).filter_by(
                    role_id=manager.id,
                    menu_id=menu.id
                ).first()

                if not exists:
                    db.add(RoleRight(
                        role_id=manager.id,
                        menu_id=menu.id,
                        can_view=can_view,
                        can_create=can_create,
                        can_edit=can_edit,
                        can_delete=can_delete,
                        created_by="System",
                        modified_by="System"
                    ))
            
            print(f"Manager: Granted access to {len(manager_access)} menus")


        # ---------------------------------------------------------
        # Commit changes
        # ---------------------------------------------------------
        db.commit()
        print("\nRole rights seeded successfully!")
        print("\nSummary:")
        print(f"   - super_admin: {db.query(RoleRight).filter_by(role_id=super_admin.id).count()} permissions")
        if org_admin:
            print(f"   - org_admin: {db.query(RoleRight).filter_by(role_id=org_admin.id).count()} permissions")
        if employee:
            print(f"   - employee: {db.query(RoleRight).filter_by(role_id=employee.id).count()} permissions")
        if manager:
            print(f"   - manager: {db.query(RoleRight).filter_by(role_id=manager.id).count()} permissions")

    except Exception as e:
        db.rollback()
        print(f"\n[Error] Error seeding role rights: {e}")
        import traceback
        traceback.print_exc()



if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_role_rights(db)
    finally:
        db.close()