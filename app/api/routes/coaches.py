from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.coach import CoachCreate, CoachUpdate, CoachOut
from app.crud import coach as coach_crud
from app.core.security import get_current_user, get_admin_user

router = APIRouter(prefix="/coaches", tags=["coaches"])

@router.get("", response_model=list[CoachOut])
def get_coaches(db: Session=Depends(get_db), _=Depends(get_current_user)):
    return coach_crud.get_all(db)

@router.post("", response_model=CoachOut)
def create_coach(data: CoachCreate, db: Session=Depends(get_db), _=Depends(get_admin_user)):
    return coach_crud.create(db, data)

@router.put("/{coach_id}", response_model=CoachOut)
def update_coach(coach_id: str, data: CoachUpdate, db: Session=Depends(get_db), _=Depends(get_admin_user)):
    coach = coach_crud.get_by_id(db, coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return coach_crud.update(db, coach, data)

@router.delete("/{coach_id}")
def delete_coach(coach_id: str, db: Session=Depends(get_db), _=Depends(get_admin_user)):
    coach = coach_crud.get_by_id(db, coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    coach_crud.delete(db, coach)
    return {"detail": "Coach deleted"}