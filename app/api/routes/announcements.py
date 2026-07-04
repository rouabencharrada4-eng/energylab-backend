from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate, AnnouncementOut
from app.crud import announcement as ann_crud
from app.core.security import get_admin_user

router = APIRouter(prefix="/announcements", tags=["announcements"])

@router.get("/active", response_model=list[AnnouncementOut])
def get_active(db: Session=Depends(get_db)):
    return ann_crud.get_active(db)

@router.get("", response_model=list[AnnouncementOut])
def get_all(db: Session=Depends(get_db), _=Depends(get_admin_user)):
    return ann_crud.get_all(db)

@router.post("", response_model=AnnouncementOut)
def create(data: AnnouncementCreate, db: Session=Depends(get_db), _=Depends(get_admin_user)):
    return ann_crud.create(db, data)

@router.put("/{ann_id}", response_model=AnnouncementOut)
def update(ann_id: str, data: AnnouncementUpdate, db: Session=Depends(get_db), _=Depends(get_admin_user)):
    ann = ann_crud.get_by_id(db, ann_id)
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return ann_crud.update(db, ann, data)

@router.delete("/{ann_id}")
def delete(ann_id: str, db: Session=Depends(get_db), _=Depends(get_admin_user)):
    ann = ann_crud.get_by_id(db, ann_id)
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    ann_crud.delete(db, ann)
    return {"detail": "Announcement deleted"}