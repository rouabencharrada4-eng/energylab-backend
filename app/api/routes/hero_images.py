# app/api/routes/hero_images.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.hero_image import HeroImageUpdate, HeroImageOut
from app.crud import hero_image as hero_crud
from app.core.security import get_admin_user
from app.core.uploads import upload_image, delete_image

router = APIRouter(prefix="/hero-images", tags=["hero-images"])


@router.get("", response_model=list[HeroImageOut])
def get_hero_images(db: Session = Depends(get_db)):
    """Public — active slideshow images only, in display order."""
    return hero_crud.get_all(db, active_only=True)


@router.get("/all", response_model=list[HeroImageOut])
def get_hero_images_all(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    """Admin — every image, including hidden, for the management screen."""
    return hero_crud.get_all(db, active_only=False)


@router.post("", response_model=HeroImageOut)
def add_hero_image(
    file: UploadFile = File(...),
    sort_order: int = Form(0),
    db: Session = Depends(get_db),
    _=Depends(get_admin_user),
):
    url = upload_image(file, folder="hero")
    return hero_crud.create(db, image_url=url, sort_order=sort_order, is_active=True)


@router.put("/{image_id}", response_model=HeroImageOut)
def update_hero_image(image_id: str, data: HeroImageUpdate, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    image = hero_crud.get_by_id(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return hero_crud.update(db, image, data)


@router.delete("/{image_id}")
def delete_hero_image(image_id: str, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    image = hero_crud.get_by_id(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    delete_image(image.image_url)
    hero_crud.delete(db, image)
    return {"detail": "Image deleted"}