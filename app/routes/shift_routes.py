from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.shift_m import Shift
from app.schema.shift_schema import ShiftCreate, ShiftUpdate, ShiftResponse
from app.models.user_m import User
from app.dependencies import get_current_user

# Permission dependencies
from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

router = APIRouter(prefix="/shifts", tags=["Shifts"])


# ---------------------- CREATE SHIFT ----------------------
@router.post(
    "/",
    response_model=ShiftResponse,
    dependencies=[Depends(require_create_permission(41))]
)
def create_shift(
    shift_in: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check duplicates (name OR code)
    exists = db.query(Shift).filter(
        (Shift.shift_name == shift_in.shift_name) |
        (Shift.shift_code == shift_in.shift_code)
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="Shift already exists")

    # FIX: Use model_dump() instead of dict()
    new_shift = Shift(
        **shift_in.model_dump(),
        created_by=current_user.id
    )

    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)

    return new_shift


# ---------------------- GET ALL SHIFTS ----------------------
@router.get(
    "/",
    response_model=List[ShiftResponse],
    dependencies=[Depends(require_view_permission(41))]
)
def get_all_shifts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Shift).all()


# ---------------------- GET SHIFT BY ID ----------------------
@router.get(
    "/{shift_id}",
    response_model=ShiftResponse,
    dependencies=[Depends(require_view_permission(41))]
)
def get_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    return shift

# ---------------------- UPDATE SHIFT ----------------------
@router.put(
    "/{shift_id}",
    response_model=ShiftResponse,
    dependencies=[Depends(require_edit_permission(41))]
)
def update_shift(
    shift_id: int,
    update: ShiftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    # FIX: Use model_dump(exclude_unset=True)
    update_data = update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(shift, key, value)

    shift.modified_by = current_user.first_name

    db.commit()
    db.refresh(shift)

    return shift


# ---------------------- DELETE SHIFT ----------------------
@router.delete(
    "/{shift_id}",
    dependencies=[Depends(require_delete_permission(41))]
)
def delete_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    db.delete(shift)
    db.commit()

    # Your test expects only: "Shift deleted successfully"
    return {"message": "Shift deleted successfully"}
