# app/seeders/super_admin.py
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user_m import User
from app.models.role_m import Role
from app.utils.utils import hash_password  # your hash_password function

def seed_super_admin(db: Session):

    try:
        # 1️⃣ Get super_admin role
        super_admin_role = db.query(Role).filter_by(name="super_admin").first()
        if not super_admin_role:
            print("[Error] Super Admin role not found. Run role_seeder first.")
            return

        # 2️⃣ Check if super admin user exists
        existing_user = db.query(User).filter_by(email="superadmin@hrms.com").first()
        if existing_user:
            print("Super Admin already exists")
            return

        # 3️⃣ Create Super Admin user (no branch, no org)
        user = User(
            first_name="Super",
            last_name="Admin",
            email="superadmin@hrms.com",
            hashed_password=hash_password("Admin@123"),  # change default password if needed
            role_id=super_admin_role.id,
            is_org_admin=False,
            created_by="system"
        )                                                                                                                                                                                                                      

        db.add(user)
        db.commit()
        print(f"Super Admin created: {user.first_name} {user.last_name}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating Super Admin: {e}")




if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_super_admin(db)
    finally:
        db.close()
