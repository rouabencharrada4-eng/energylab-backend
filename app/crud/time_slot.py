from sqlalchemy.orm import Session, joinedload
from app.db.models import TimeSlot, Booking, BookingStatusEnum
from app.schemas.time_slot import TimeSlotCreate, TimeSlotUpdate

def get_all(db: Session, service_id: str = None, coach_id: str = None):
    q = db.query(TimeSlot).options(
        joinedload(TimeSlot.service),
        joinedload(TimeSlot.coach),
    )
    if service_id:
        q = q.filter(TimeSlot.service_id == service_id)
    if coach_id:
        q = q.filter(TimeSlot.coach_id == coach_id)
    return q.filter(TimeSlot.is_active == True).order_by(TimeSlot.date, TimeSlot.start_time).all()

def get_by_id(db: Session, slot_id: str):
    return db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()

def get_accepted_count(db: Session, slot_id: str) -> int:
    return (
        db.query(Booking)
        .filter(Booking.time_slot_id == slot_id, Booking.status == BookingStatusEnum.accepted)
        .count()
    )

def create(db: Session, data: TimeSlotCreate):
    slot = TimeSlot(**data.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot

def update(db: Session, slot: TimeSlot, data: TimeSlotUpdate):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(slot, field, value)
    db.commit()
    db.refresh(slot)
    return slot

def delete(db: Session, slot: TimeSlot):
    db.delete(slot)
    db.commit()