from sqlalchemy.orm import Session
from app.db.models import Coach, CoachService, Service
from app.schemas.coach import CoachCreate, CoachUpdate

def get_all(db: Session):
    return db.query(Coach).order_by(Coach.full_name).all()

def get_by_id(db: Session, coach_id: str):
    return db.query(Coach).filter(Coach.id == coach_id).first()

def create(db: Session, data: CoachCreate):
    coach = Coach(full_name=data.full_name, bio=data.bio, is_active=data.is_active)
    db.add(coach)
    db.flush()
    for sid in data.service_ids:
        db.add(CoachService(coach_id=coach.id, service_id=sid))
    db.commit()
    db.refresh(coach)
    return coach

def update(db: Session, coach: Coach, data: CoachUpdate):
    for field, value in data.model_dump(exclude_none=True, exclude={"service_ids"}).items():
        setattr(coach, field, value)
    if data.service_ids is not None:
        db.query(CoachService).filter(CoachService.coach_id == coach.id).delete()
        for sid in data.service_ids:
            db.add(CoachService(coach_id=coach.id, service_id=sid))
    db.commit()
    db.refresh(coach)
    return coach

def delete(db: Session, coach: Coach):
    db.delete(coach)
    db.commit()