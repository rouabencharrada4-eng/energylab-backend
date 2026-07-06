from sqlalchemy.orm import Session, joinedload
from app.db.models import Booking, BookingStatusEnum, TimeSlot, Service
from app.schemas.booking import BookingCreate, BookingStatusUpdate
from app import crud
from fastapi import HTTPException, status

def _with_relations(q):
    return q.options(
        joinedload(Booking.customer),
        joinedload(Booking.time_slot).joinedload(TimeSlot.service),
        joinedload(Booking.time_slot).joinedload(TimeSlot.coach),
    )

def get_all(db: Session):
    return _with_relations(db.query(Booking)).order_by(Booking.created_at.desc()).all()

def get_by_customer(db: Session, customer_id: str):
    return (
        _with_relations(db.query(Booking))
        .filter(Booking.customer_id == customer_id)
        .order_by(Booking.created_at.desc())
        .all()
    )

def get_by_id(db: Session, booking_id: str):
    return _with_relations(db.query(Booking)).filter(Booking.id == booking_id).first()

def create(db: Session, data: BookingCreate, customer_id: str):
    slot = crud.time_slot.get_by_id(db, data.time_slot_id)
    if not slot or not slot.is_active:
        raise HTTPException(status_code=400, detail="Time slot not available")

    capacity = slot.capacity if slot.capacity is not None else slot.service.max_capacity
    accepted = crud.time_slot.get_accepted_count(db, slot.id)
    if accepted >= capacity:
        raise HTTPException(status_code=400, detail="This time slot is fully booked")

    booking = Booking(
        customer_id=customer_id,
        time_slot_id=data.time_slot_id,
        customer_phone=data.customer_phone,
        customer_notes=data.customer_notes,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return get_by_id(db, booking.id)

def update_status(db: Session, booking: Booking, data: BookingStatusUpdate):
    if data.status == BookingStatusEnum.accepted:
        slot     = booking.time_slot
        capacity = slot.capacity if slot.capacity is not None else slot.service.max_capacity
        accepted = crud.time_slot.get_accepted_count(db, slot.id)
        if accepted >= capacity:
            raise HTTPException(status_code=400, detail="Slot is at capacity — cannot accept more bookings")

    booking.status = data.status
    if data.admin_notes is not None:
        booking.admin_notes = data.admin_notes
    db.commit()
    db.refresh(booking)
    return booking