# app/api/routes/showcase.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.showcase import ShowcaseItemCreate, ShowcaseItemUpdate, ShowcaseItemOut
from app.crud import showcase as showcase_crud
from app.core.security import get_admin_user
from app.core.uploads import upload_image

router = APIRouter(prefix="/showcase", tags=["showcase"])


@router.get("", response_model=list[ShowcaseItemOut])
def get_showcase(db: Session = Depends(get_db)):
    """Public — active cards only, in display order."""
    return showcase_crud.get_all(db, active_only=True)


@router.get("/all", response_model=list[ShowcaseItemOut])
def get_showcase_all(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    return showcase_crud.get_all(db, active_only=False)


@router.post("", response_model=ShowcaseItemOut)
def create_item(data: ShowcaseItemCreate, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    return showcase_crud.create(db, data)


@router.put("/{item_id}", response_model=ShowcaseItemOut)
def update_item(item_id: str, data: ShowcaseItemUpdate, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    item = showcase_crud.get_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Showcase item not found")
    return showcase_crud.update(db, item, data)


@router.delete("/{item_id}")
def delete_item(item_id: str, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    item = showcase_crud.get_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Showcase item not found")
    showcase_crud.delete(db, item)
    return {"detail": "Showcase item deleted"}


@router.post("/{item_id}/image", response_model=ShowcaseItemOut)
def upload_item_image(
    item_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(get_admin_user),
):
    item = showcase_crud.get_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Showcase item not found")
    item.image_url = upload_image(file, folder="showcase")
    db.commit()
    db.refresh(item)
    return item