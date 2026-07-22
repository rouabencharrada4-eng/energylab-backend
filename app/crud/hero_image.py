# app/crud/hero_image.py
from sqlalchemy.orm import Session
from app.db.models import HeroImage
from app.schemas.hero_image import HeroImageUpdate


def get_all(db: Session, active_only: bool = False):
    q = db.query(HeroImage)
    if active_only:
        q = q.filter(HeroImage.is_active == True)
    return q.order_by(HeroImage.sort_order.asc(), HeroImage.created_at.asc()).all()


def get_by_id(db: Session, image_id: str):
    return db.query(HeroImage).filter(HeroImage.id == image_id).first()


def create(db: Session, image_url: str, sort_order: int, is_active: bool):
    img = HeroImage(image_url=image_url, sort_order=sort_order, is_active=is_active)
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


def update(db: Session, image: HeroImage, data: HeroImageUpdate):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(image, field, value)
    db.commit()
    db.refresh(image)
    return image


def delete(db: Session, image: HeroImage):
    db.delete(image)
    db.commit()