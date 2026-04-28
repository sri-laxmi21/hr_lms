# app/routes/notification_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Dict

from app.models.notification_m import Notification
from app.models.user_m import User
from app.models.candidate_m import Candidate
from app.models.job_posting_m import JobPosting
from app.database import get_db
from app.dependencies import get_current_user

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])
MENU_ID = 62   # Permission Menu ID


# -----------------------------------------------------------
# GET ALL NOTIFICATIONS FOR LOGGED-IN USER (VIEW PERMISSION)
# -----------------------------------------------------------
@router.get(
    "/",
    response_model=List[Dict],
    dependencies=[Depends(require_view_permission(MENU_ID))]
)
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifications = (
        db.query(Notification)
        .options(
            joinedload(Notification.candidate)
                .joinedload(Candidate.job_posting)
                .joinedload(JobPosting.job_description)
        )
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    result = []

    for note in notifications:
        candidate_name = None
        job_title = None

        if note.candidate:
            candidate_name = f"{note.candidate.first_name} {note.candidate.last_name}"

            if note.candidate.job_posting and note.candidate.job_posting.job_description:
                job_title = note.candidate.job_posting.job_description.title

        result.append({
            "notification_id": note.id,
            "message": note.message,
            "is_read": note.is_read,
            "created_at": note.created_at,
            "candidate_name": candidate_name,
            "job_title": job_title
        })

    return result


# -----------------------------------------------------------
# MARK NOTIFICATION AS READ (EDIT PERMISSION)
# -----------------------------------------------------------
@router.put(
    "/{notification_id}/read",
    response_model=Dict,
    dependencies=[Depends(require_edit_permission(MENU_ID))]
)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
        .first()
    )

    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")

    note.is_read = True
    db.commit()
    db.refresh(note)

    return {"notification_id": note.id, "is_read": note.is_read}


# -----------------------------------------------------------
# DELETE NOTIFICATION (DELETE PERMISSION)
# -----------------------------------------------------------
@router.delete(
    "/{notification_id}",
    response_model=Dict,
    dependencies=[Depends(require_delete_permission(MENU_ID))]
)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
        .first()
    )

    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(note)
    db.commit()

    return {"detail": "Notification deleted successfully"}
