# app/crud/gallery.py
from sqlalchemy.orm import Session
from app.db.models import GalleryImage
from app.schemas.gallery import GalleryImageUpdate


def get_all(db: Session, active_only: bool = False):
    q = db.query(GalleryImage)
    if active_only:
        q = q.filter(GalleryImage.is_active == True)
    return q.order_by(GalleryImage.sort_order.asc(), GalleryImage.created_at.asc()).all()


def get_by_id(db: Session, image_id: str):
    return db.query(GalleryImage).filter(GalleryImage.id == image_id).first()


def create(db: Session, image_url: str, caption: str | None, sort_order: int, is_active: bool):
    img = GalleryImage(image_url=image_url, caption=caption, sort_order=sort_order, is_active=is_active)
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


def update(db: Session, image: GalleryImage, data: GalleryImageUpdate):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(image, field, value)
    db.commit()
    db.refresh(image)
    return image


def delete(db: Session, image: GalleryImage):
    db.delete(image)
    db.commit()