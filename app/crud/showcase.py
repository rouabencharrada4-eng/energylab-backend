# app/crud/showcase.py
from sqlalchemy.orm import Session
from app.db.models import ShowcaseItem
from app.schemas.showcase import ShowcaseItemCreate, ShowcaseItemUpdate


def get_all(db: Session, active_only: bool = False):
    q = db.query(ShowcaseItem)
    if active_only:
        q = q.filter(ShowcaseItem.is_active == True)
    return q.order_by(ShowcaseItem.sort_order.asc(), ShowcaseItem.created_at.asc()).all()


def get_by_id(db: Session, item_id: str):
    return db.query(ShowcaseItem).filter(ShowcaseItem.id == item_id).first()


def create(db: Session, data: ShowcaseItemCreate):
    item = ShowcaseItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update(db: Session, item: ShowcaseItem, data: ShowcaseItemUpdate):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, item: ShowcaseItem):
    db.delete(item)
    db.commit()