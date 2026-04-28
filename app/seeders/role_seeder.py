# app/seeders/seed_roles.py

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.role_m import Role

def seed_roles(db: Session):
    roles = [
        "super_admin",
        "org_admin",
        "employee",
        "manager"
    ]

    for role_name in roles:
        existing = db.query(Role).filter_by(name=role_name).first()
        if not existing:
            db.add(Role(name=role_name))
    db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()
