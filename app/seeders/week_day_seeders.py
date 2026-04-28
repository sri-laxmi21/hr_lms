# app/seeders/seed_weekdays.py
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.week_day_m import WeekDay

def seed_weekdays(db: Session):
    weekdays = [
        {"id": 1, "week_name": "Monday"},
        {"id": 2, "week_name": "Tuesday"},
        {"id": 3, "week_name": "Wednesday"},
        {"id": 4, "week_name": "Thursday"},
        {"id": 5, "week_name": "Friday"},
        {"id": 6, "week_name": "Saturday"},
        {"id": 7, "week_name": "Sunday"}
    ]

    for day in weekdays:
        existing = db.query(WeekDay).filter_by(week_name=day["week_name"]).first()
        if not existing:
            db.add(WeekDay(**day))

    db.commit()

    print("Weekdays seeded successfully!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_weekdays(db)
    finally:
        db.close()

