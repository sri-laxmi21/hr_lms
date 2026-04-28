from fastapi import FastAPI
from app.database import SessionLocal
from app.models.module_m import Module
from sqlalchemy.orm import Session

def seed_modules(db: Session):
    modules = [
        {"id": 1, "name": "base", "display_name": "Base"},
        {"id": 2, "name": "hrms", "display_name": "HRMS"},
        {"id": 3, "name": "lms", "display_name": "LMS"},
        {"id": 4, "name": "hiring", "display_name": "Hiring"},
    ]

    for m in modules:
        exists = db.query(Module).filter_by(id=m["id"]).first()
        if not exists:
            db.add(Module(**m))
    db.commit()

app = FastAPI()

@app.on_event("startup")
def startup_event():
    db = SessionLocal()  # ✅ create DB session
    try:
        seed_modules(db)  # ✅ pass db to seed_modules
        print("Modules seeded successfully")
    except Exception as e:
        print(f"Error seeding modules: {e}")
    finally:
        db.close()  # ✅ always close DB session
