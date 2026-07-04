from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.time_slot import TimeSlotCreate, TimeSlotUpdate, TimeSlotOut
from app.crud import time_slot as slot_crud
from app.core.security import get_current_user, get_admin_user

router = APIRouter(prefix="/time-slots", tags=["time-slots"])

@router.get("", response_model=list[TimeSlotOut])
def get_slots(
    service_id: Optional[str] = Query(None),
    coach_id:   Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return slot_crud.get_all(db, service_id=service_id, coach_id=coach_id)

@router.post("", response_model=TimeSlotOut)
def create_slot(data: TimeSlotCreate, db: Session=Depends(get_db), _=Depends(get_admin_user)):
    return slot_crud.create(db, data)

@router.put("/{slot_id}", response_model=TimeSlotOut)
def update_slot(slot_id: str, data: TimeSlotUpdate, db: Session=Depends(get_db), _=Depends(get_admin_user)):
    slot = slot_crud.get_by_id(db, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    return slot_crud.update(db, slot, data)

@router.delete("/{slot_id}")
def delete_slot(slot_id: str, db: Session=Depends(get_db), _=Depends(get_admin_user)):
    slot = slot_crud.get_by_id(db, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    slot_crud.delete(db, slot)
    return {"detail": "Time slot deleted"}