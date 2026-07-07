# app/api/routes/site_content.py
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.site_content import SiteContentBulkUpdate, SiteContentOut
from app.crud import site_content as content_crud
from app.core.security import get_admin_user
from app.core.uploads import upload_image

router = APIRouter(prefix="/site-content", tags=["site-content"])


@router.get("", response_model=SiteContentOut)
def get_content(db: Session = Depends(get_db)):
    """Public — the homepage reads all editable copy/images from here."""
    return {"values": content_crud.get_all(db)}


@router.put("", response_model=SiteContentOut)
def update_content(data: SiteContentBulkUpdate, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    """Admin — bulk upsert any subset of keys, e.g. {'hero_title': 'New Title'}."""
    return {"values": content_crud.bulk_upsert(db, data.values)}


@router.post("/image")
def upload_content_image(
    key: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(get_admin_user),
):
    """
    Admin — upload an image for a given content key (e.g. key=hero_bg_url)
    and store the resulting URL under that key in one step.
    """
    url = upload_image(file, folder="site-content")
    content_crud.bulk_upsert(db, {key: url})
    return {"key": key, "url": url}