# app/api/routes/gallery.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.gallery import GalleryImageUpdate, GalleryImageOut
from app.crud import gallery as gallery_crud
from app.core.security import get_admin_user
from app.core.uploads import upload_image, delete_image

router = APIRouter(prefix="/gallery", tags=["gallery"])


@router.get("", response_model=list[GalleryImageOut])
def get_gallery(db: Session = Depends(get_db)):
    """Public — active images only, in display order."""
    return gallery_crud.get_all(db, active_only=True)


@router.get("/all", response_model=list[GalleryImageOut])
def get_gallery_all(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    """Admin — every image, including inactive, for the management screen."""
    return gallery_crud.get_all(db, active_only=False)


@router.post("", response_model=GalleryImageOut)
def add_image(
    file: UploadFile = File(...),
    caption: str = Form(""),
    sort_order: int = Form(0),
    db: Session = Depends(get_db),
    _=Depends(get_admin_user),
):
    url = upload_image(file, folder="gallery")
    return gallery_crud.create(db, image_url=url, caption=caption or None, sort_order=sort_order, is_active=True)


@router.put("/{image_id}", response_model=GalleryImageOut)
def update_image(image_id: str, data: GalleryImageUpdate, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    image = gallery_crud.get_by_id(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return gallery_crud.update(db, image, data)


@router.delete("/{image_id}")
def delete_image_route(image_id: str, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    image = gallery_crud.get_by_id(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    delete_image(image.image_url)
    gallery_crud.delete(db, image)
    return {"detail": "Image deleted"}