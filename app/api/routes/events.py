# app/api/routes/events.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.event import EventCreate, EventUpdate, EventOut
from app.crud import event as event_crud
from app.core.security import get_admin_user
from app.core.uploads import upload_image, delete_image

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/active", response_model=list[EventOut])
def get_active(db: Session = Depends(get_db)):
    """Public — active events, soonest first. The homepage shows the first one."""
    return event_crud.get_active(db)


@router.get("", response_model=list[EventOut])
def get_all(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    return event_crud.get_all(db)


@router.post("", response_model=EventOut)
def create(data: EventCreate, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    return event_crud.create(db, data)


@router.put("/{event_id}", response_model=EventOut)
def update(event_id: str, data: EventUpdate, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    event = event_crud.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event_crud.update(db, event, data)


@router.delete("/{event_id}")
def delete(event_id: str, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    event = event_crud.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.image_url:
        delete_image(event.image_url)
    event_crud.delete(db, event)
    return {"detail": "Event deleted"}


@router.post("/{event_id}/image", response_model=EventOut)
def upload_event_image(
    event_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(get_admin_user),
):
    event = event_crud.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.image_url:
        delete_image(event.image_url)
    event.image_url = upload_image(file, folder="events")
    db.commit()
    db.refresh(event)
    return event