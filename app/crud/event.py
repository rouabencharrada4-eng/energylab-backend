# app/crud/event.py
from sqlalchemy import case
from sqlalchemy.orm import Session
from app.db.models import Event
from app.schemas.event import EventCreate, EventUpdate


def get_all(db: Session):
    """Admin — every event, newest first."""
    return db.query(Event).order_by(Event.created_at.desc()).all()


def get_active(db: Session):
    """Public — active events, soonest upcoming date first; undated events last."""
    return (
        db.query(Event)
        .filter(Event.is_active == True)
        .order_by(
            case((Event.event_date.is_(None), 1), else_=0),  # dated events first, undated last
            Event.event_date.asc(),
            Event.created_at.desc(),
        )
        .all()
    )


def get_by_id(db: Session, event_id: str):
    return db.query(Event).filter(Event.id == event_id).first()


def create(db: Session, data: EventCreate):
    event = Event(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def update(db: Session, event: Event, data: EventUpdate):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


def delete(db: Session, event: Event):
    db.delete(event)
    db.commit()