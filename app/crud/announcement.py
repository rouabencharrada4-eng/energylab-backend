from sqlalchemy.orm import Session
from app.db.models import Announcement
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate
from datetime import datetime

def get_all(db: Session):
    return db.query(Announcement).order_by(Announcement.created_at.desc()).all()

def get_active(db: Session):
    now = datetime.utcnow()
    return (
        db.query(Announcement)
        .filter(
            Announcement.is_active == True,
            (Announcement.starts_at == None) | (Announcement.starts_at <= now),
            (Announcement.ends_at   == None) | (Announcement.ends_at   >= now),
        )
        .order_by(Announcement.created_at.desc())
        .all()
    )

def get_by_id(db: Session, ann_id: str):
    return db.query(Announcement).filter(Announcement.id == ann_id).first()

def create(db: Session, data: AnnouncementCreate):
    ann = Announcement(**data.model_dump())
    db.add(ann)
    db.commit()
    db.refresh(ann)
    return ann

def update(db: Session, ann: Announcement, data: AnnouncementUpdate):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(ann, field, value)
    db.commit()
    db.refresh(ann)
    return ann

def delete(db: Session, ann: Announcement):
    db.delete(ann)
    db.commit()