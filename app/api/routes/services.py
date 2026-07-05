from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
import shutil, uuid
from app.db.database import get_db
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceOut
from app.crud import service as service_crud
from app.core.security import get_admin_user
from app.core.config import settings

router = APIRouter(prefix="/services", tags=["services"])

UPLOAD_DIR = Path("uploads/services")

@router.get("", response_model=list[ServiceOut])
def get_services(db: Session=Depends(get_db)):
    return service_crud.get_all(db)

@router.post("", response_model=ServiceOut)
def create_service(data: ServiceCreate, db: Session=Depends(get_db), _=Depends(get_admin_user)):
    return service_crud.create(db, data)

@router.put("/{service_id}", response_model=ServiceOut)
def update_service(service_id: str, data: ServiceUpdate, db: Session=Depends(get_db), _=Depends(get_admin_user)):
    service = service_crud.get_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service_crud.update(db, service, data)

@router.delete("/{service_id}")
def delete_service(service_id: str, db: Session=Depends(get_db), _=Depends(get_admin_user)):
    service = service_crud.get_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service_crud.delete(db, service)
    return {"detail": "Service deleted"}

@router.post("/{service_id}/image", response_model=ServiceOut)
def upload_service_image(
    service_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(get_admin_user),
):
    service = service_crud.get_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=400, detail="File must be an image (jpeg, png, or webp)")

    ext = file.filename.split(".")[-1]
    filename = f"{service_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = UPLOAD_DIR / filename

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    service.image_url = f"{settings.BACKEND_URL}/uploads/services/{filename}"
    db.commit()
    db.refresh(service)
    return service